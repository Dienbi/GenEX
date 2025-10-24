from __future__ import annotations
from django.shortcuts import render, redirect
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import sys

from .models import VoiceEvaluation, ReferenceText, VoiceEvaluationHistory, Certificate, PronunciationPractice, TestingCenter

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
from .serializers import (
    VoiceEvaluationSerializer, 
    VoiceEvaluationCreateSerializer,
    VoiceEvaluationDetailSerializer,
    ReferenceTextSerializer,
    VoiceEvaluationHistorySerializer,
    CertificateSerializer,
    PronunciationPracticeSerializer,
    TestingCenterSerializer
)
from .ai_service import voice_service
from .certificate_service import certificate_generator
from .pronunciation_service import pronunciation_service
from .map_service import map_service


class VoiceEvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet for voice evaluations"""
    serializer_class = VoiceEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Users can only see their own evaluations"""
        user = self.request.user
        if user.is_staff:
            return VoiceEvaluation.objects.all()
        return VoiceEvaluation.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VoiceEvaluationCreateSerializer
        elif self.action == 'retrieve':
            return VoiceEvaluationDetailSerializer
        return VoiceEvaluationSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new voice evaluation and process it"""
        import traceback
        import sys
        import logging
        
        # Setup logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        
        logger.error("="*80)
        logger.error("CREATE METHOD CALLED")
        logger.error(f"Request data keys: {request.data.keys() if hasattr(request.data, 'keys') else 'N/A'}")
        logger.error(f"Request user: {request.user}")
        logger.error("="*80)
        
        print("="*80, file=sys.stderr)
        print("CREATE METHOD CALLED", file=sys.stderr)
        print(f"Request data: {request.data}", file=sys.stderr)
        print(f"Request user: {request.user}", file=sys.stderr)
        print("="*80, file=sys.stderr)
        sys.stderr.flush()
        
        try:
            logger.error("Step 1: Getting serializer")
            print("Step 1: Getting serializer", file=sys.stderr)
            serializer = self.get_serializer(data=request.data)
            print(f"Serializer class: {serializer.__class__.__name__}", file=sys.stderr)
            
            logger.error("Step 2: Validating serializer")
            print("Step 2: Validating serializer", file=sys.stderr)
            serializer.is_valid(raise_exception=True)
            print(f"Validated data: {serializer.validated_data}", file=sys.stderr)
            
            logger.error("Step 3: Saving evaluation")
            print("Step 3: Saving evaluation", file=sys.stderr)
            # Create the evaluation object
            evaluation = serializer.save(user=request.user, processing_status='pending')
            print(f"Step 4: Evaluation created with ID: {evaluation.id}", file=sys.stderr)
            sys.stderr.flush()
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error("="*80)
            logger.error("ERROR IN CREATE BEFORE PROCESSING:")
            logger.error(error_details)
            logger.error("="*80)
            print("="*80, file=sys.stderr)
            print("ERROR IN CREATE BEFORE PROCESSING:", file=sys.stderr)
            print(error_details, file=sys.stderr)
            print("="*80, file=sys.stderr)
            sys.stderr.flush()
            return Response(
                {'error': f'Creation failed: {str(e)}', 'details': error_details},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Process the audio asynchronously (or synchronously for now)
        try:
            print("Step 5: Starting processing")
            self._process_evaluation(evaluation)
            evaluation.processing_status = 'completed'
            evaluation.save()
            print("Step 6: Processing completed successfully")
        except Exception as e:
            error_details = traceback.format_exc()
            print("="*80)
            print("ERROR DURING PROCESSING:")
            print(error_details)
            print("="*80)
            sys.stdout.flush()
            evaluation.processing_status = 'failed'
            evaluation.error_message = str(e)
            evaluation.save()
            return Response(
                {'error': f'Processing failed: {str(e)}', 'details': error_details},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Return the completed evaluation
        print("Step 7: Serializing response")
        output_serializer = VoiceEvaluationDetailSerializer(evaluation)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def _process_evaluation(self, evaluation):
        """Process the voice evaluation"""
        import traceback
        
        try:
            evaluation.processing_status = 'processing'
            evaluation.save()
            
            audio_path = evaluation.audio_file.path
            language = evaluation.language
            
            print(f"Processing evaluation: {evaluation.id}")
            print(f"Audio path: {audio_path}")
            print(f"Language: {language}")
            
        except Exception as e:
            print(f"Error in _process_evaluation setup: {traceback.format_exc()}")
            raise
        
        # Step 1: Transcribe audio
        transcription_result = voice_service.transcribe_audio(audio_path, language)
        if not transcription_result.get('success'):
            raise Exception(f"Transcription failed: {transcription_result.get('error')}")
        
        evaluation.transcription = transcription_result['text']
        
        # Check transcription quality
        quality_issues = transcription_result.get('quality_issues', [])
        confidence = transcription_result.get('confidence', 1.0)
        
        # Step 2: Analyze verbal communication (pass quality issues)
        verbal_result = voice_service.analyze_verbal_communication(
            transcription_result['text'],
            language,
            quality_issues=quality_issues
        )
        evaluation.fluency_score = verbal_result['fluency_score']
        evaluation.vocabulary_score = verbal_result['vocabulary_score']
        evaluation.structure_score = verbal_result['structure_score']
        evaluation.verbal_score = verbal_result['verbal_score']
        
        # Store quality warnings in feedback
        if 'quality_warning' in verbal_result:
            if not evaluation.feedback:
                evaluation.feedback = {}
            evaluation.feedback['transcription_quality'] = {
                'confidence': round(confidence * 100, 1),
                'issues': quality_issues,
                'warning': verbal_result['quality_warning']
            }
        
        # Step 3: Analyze paraverbal communication
        paraverbal_result = voice_service.analyze_paraverbal_communication(audio_path)
        if paraverbal_result.get('success'):
            evaluation.pitch_score = paraverbal_result['pitch_score']
            evaluation.pace_score = paraverbal_result['pace_score']
            evaluation.energy_score = paraverbal_result['energy_score']
            evaluation.paraverbal_score = paraverbal_result['paraverbal_score']
            evaluation.duration = paraverbal_result['duration']
            evaluation.audio_features = paraverbal_result['audio_features']
        
        # Step 4: Check originality
        reference_texts = ReferenceText.objects.filter(language=language).values(
            'theme', 'text', 'embedding', 'language'
        )
        originality_result = voice_service.check_originality(
            transcription_result['text'],
            language,
            list(reference_texts)
        )
        if originality_result.get('success'):
            evaluation.originality_score = originality_result['originality_score']
        
        # Step 5: Calculate total score
        # Weights: Verbal 40%, Paraverbal 30%, Originality 30%
        evaluation.total_score = (
            evaluation.verbal_score * 0.4 +
            evaluation.paraverbal_score * 0.3 +
            evaluation.originality_score * 0.3
        )
        
        # Step 6: Determine language level
        scores = {
            'total_score': evaluation.total_score,
            'verbal_score': evaluation.verbal_score,
            'paraverbal_score': evaluation.paraverbal_score,
            'originality_score': evaluation.originality_score,
            'fluency_score': evaluation.fluency_score,
            'vocabulary_score': evaluation.vocabulary_score,
            'structure_score': evaluation.structure_score,
            'pitch_score': evaluation.pitch_score,
            'pace_score': evaluation.pace_score,
        }
        evaluation.estimated_level = voice_service.calculate_language_level(scores)
        
        # Step 7: Generate feedback
        evaluation.feedback = voice_service.generate_feedback(scores, language)
        
        # Step 8: Update user's level if improved
        user = evaluation.user
        old_level = user.level
        
        # Update user level based on evaluation
        level_mapping = {'A1': 'weak', 'A2': 'weak', 'B1': 'medium', 'B2': 'medium', 'C1': 'advanced', 'C2': 'advanced'}
        new_level = level_mapping.get(evaluation.estimated_level, user.level)
        
        if new_level != old_level:
            user.level = new_level
            user.save()
            
            # Create history record
            VoiceEvaluationHistory.objects.create(
                user=user,
                evaluation=evaluation,
                previous_level=old_level,
                new_level=new_level,
                improvement_score=evaluation.total_score
            )
        
        evaluation.save()
    
    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Get user's evaluation history and progress"""
        user = request.user
        evaluations = VoiceEvaluation.objects.filter(
            user=user,
            processing_status='completed'
        ).order_by('-created_at')[:10]
        
        history = VoiceEvaluationHistory.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Calculate statistics
        if evaluations.exists():
            avg_score = sum(e.total_score for e in evaluations) / len(evaluations)
            latest_score = evaluations[0].total_score
            improvement = latest_score - evaluations[-1].total_score if len(evaluations) > 1 else 0
        else:
            avg_score = 0
            latest_score = 0
            improvement = 0
        
        return Response({
            'evaluations': VoiceEvaluationSerializer(evaluations, many=True).data,
            'history': VoiceEvaluationHistorySerializer(history, many=True).data,
            'statistics': {
                'total_evaluations': evaluations.count(),
                'average_score': round(avg_score, 2),
                'latest_score': round(latest_score, 2),
                'improvement': round(improvement, 2),
                'current_level': user.level or 'Not set'
            }
        })


class ReferenceTextViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reference texts"""
    queryset = ReferenceText.objects.all()
    serializer_class = ReferenceTextSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        """Create reference text with automatic embedding generation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate embedding
        text = serializer.validated_data['text']
        embedding = voice_service.generate_text_embedding(text)
        
        # Save with embedding
        reference = serializer.save(embedding=embedding)
        
        return Response(
            ReferenceTextSerializer(reference).data,
            status=status.HTTP_201_CREATED
        )


# Traditional Django views for web interface
@login_required
def voice_eval_home(request):
    """Home page for voice evaluation"""
    evaluations = VoiceEvaluation.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'evaluations': evaluations,
        'user': request.user
    }
    return render(request, 'voice_eval/home.html', context)


@login_required
def voice_eval_detail(request, pk):
    """Detail page for a specific evaluation"""
    from django.http import Http404
    
    try:
        evaluation = VoiceEvaluation.objects.get(pk=pk, user=request.user)
    except VoiceEvaluation.DoesNotExist:
        raise Http404("Evaluation not found")
    
    context = {
        'evaluation': evaluation,
    }
    return render(request, 'voice_eval/detail.html', context)


@login_required
def voice_eval_record(request):
    """Page for recording or uploading voice"""
    return render(request, 'voice_eval/record.html')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_supported_languages(request):
    """Get list of supported languages"""
    return Response({
        'languages': [
            {'code': 'en', 'name': 'English'},
            {'code': 'fr', 'name': 'French'}
        ]
    })


# Certificate views
@login_required
def generate_certificate_view(request, evaluation_id):
    """Generate certificate for high-scoring evaluation"""
    from django.http import Http404, HttpResponse
    from django.contrib import messages
    from django.core.files.base import ContentFile
    
    try:
        evaluation = VoiceEvaluation.objects.get(pk=evaluation_id, user=request.user)
    except VoiceEvaluation.DoesNotExist:
        raise Http404("Evaluation not found")
    
    # Check if score qualifies for certificate (70+)
    if evaluation.total_score < 70:
        messages.error(request, 'Certificate is only available for scores of 70 or higher.')
        return redirect('voice_eval:detail', pk=evaluation_id)
    
    # Check if certificate already exists
    try:
        certificate = Certificate.objects.get(evaluation=evaluation)
        # If certificate exists but no PDF file, regenerate it
        if not certificate.pdf_file:
            try:
                pdf_buffer = certificate_generator.generate_certificate(
                    request.user,
                    evaluation,
                    certificate.certificate_id
                )
                filename = f'certificate_{certificate.certificate_id}.pdf'
                pdf_content = pdf_buffer.read()
                
                if len(pdf_content) == 0:
                    raise Exception("PDF generation produced empty file")
                
                certificate.pdf_file.save(filename, ContentFile(pdf_content), save=True)
                print(f"Certificate regenerated: {certificate.pdf_file.name}, Size: {len(pdf_content)} bytes")
            except Exception as e:
                print(f"Error regenerating certificate: {str(e)}")
                import traceback
                traceback.print_exc()
                raise Http404(f"Error generating certificate: {str(e)}")
    except Certificate.DoesNotExist:
        # Generate new certificate
        certificate = Certificate.objects.create(
            user=request.user,
            evaluation=evaluation,
            language=evaluation.language,
            level=evaluation.estimated_level,
            score=evaluation.total_score
        )
        
        # Generate PDF
        try:
            pdf_buffer = certificate_generator.generate_certificate(
                request.user,
                evaluation,
                certificate.certificate_id
            )
            
            # Save PDF
            filename = f'certificate_{certificate.certificate_id}.pdf'
            pdf_content = pdf_buffer.read()
            
            if len(pdf_content) == 0:
                raise Exception("PDF generation produced empty file")
            
            certificate.pdf_file.save(filename, ContentFile(pdf_content), save=True)
            print(f"Certificate saved: {certificate.pdf_file.name}, Size: {len(pdf_content)} bytes")
        except Exception as e:
            print(f"Error generating certificate: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Http404(f"Error generating certificate: {str(e)}")
    
    # Return PDF response
    if certificate.pdf_file and certificate.pdf_file.name:
        try:
            pdf_file = certificate.pdf_file.open('rb')
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="GenEx_Certificate_{request.user.username}.pdf"'
            pdf_file.close()
            return response
        except Exception as e:
            raise Http404(f"Error reading certificate file: {str(e)}")
    else:
        raise Http404("Certificate file not found")


@login_required
def certificate_map_view(request, evaluation_id):
    """Show map of testing centers for certificate"""
    from django.http import Http404
    from django.contrib import messages
    
    try:
        evaluation = VoiceEvaluation.objects.get(pk=evaluation_id, user=request.user)
    except VoiceEvaluation.DoesNotExist:
        raise Http404("Evaluation not found")
    
    # Check if score qualifies
    if evaluation.total_score < 70:
        messages.error(request, 'Testing centers are only available for scores of 70 or higher.')
        return redirect('voice_eval:detail', pk=evaluation_id)
    
    # Get testing centers for this language
    # Filter in Python since SQLite doesn't support JSONField contains
    all_centers = TestingCenter.objects.filter(is_active=True)
    centers_list = [c for c in all_centers if evaluation.language in c.languages]
    
    # Generate map (pass list, not QuerySet)
    map_html = map_service.generate_map(centers_list)
    
    context = {
        'evaluation': evaluation,
        'map_html': map_html,
        'centers': centers_list
    }
    return render(request, 'voice_eval/certificate_map.html', context)


# Pronunciation practice views
@login_required
def pronunciation_practice_view(request, evaluation_id=None):
    """Pronunciation practice interface"""
    evaluation = None
    if evaluation_id:
        try:
            evaluation = VoiceEvaluation.objects.get(pk=evaluation_id, user=request.user)
        except VoiceEvaluation.DoesNotExist:
            pass
    
    # Get practice texts
    language = evaluation.language if evaluation else 'en'
    difficulty = 'easy' if not evaluation or evaluation.total_score < 50 else \
                 'medium' if evaluation.total_score < 70 else 'hard'
    
    practice_texts = pronunciation_service.get_practice_texts(language, difficulty)
    
    # Get user's practice history
    recent_practices = PronunciationPractice.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'evaluation': evaluation,
        'practice_texts': practice_texts,
        'recent_practices': recent_practices,
        'language': language,
        'difficulty': difficulty
    }
    return render(request, 'voice_eval/pronunciation_practice.html', context)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_pronunciation_api(request):
    """Process pronunciation practice submission"""
    expected_text = request.data.get('expected_text')
    audio_file = request.FILES.get('audio_file')
    evaluation_id = request.data.get('evaluation_id')
    language = request.data.get('language', 'en')
    
    if not expected_text or not audio_file:
        return Response(
            {'error': 'Expected text and audio file are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Save audio file temporarily
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        for chunk in audio_file.chunks():
            temp_file.write(chunk)
        temp_path = temp_file.name
    
    try:
        # Transcribe audio
        transcription_result = pronunciation_service.transcribe_audio(temp_path, language)
        
        if not transcription_result['success']:
            return Response(
                {'error': transcription_result.get('error', 'Transcription failed')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        spoken_text = transcription_result['text']
        
        # Compare texts
        comparison_result = pronunciation_service.compare_texts(expected_text, spoken_text)
        
        # Create pronunciation practice record
        practice = PronunciationPractice.objects.create(
            user=request.user,
            evaluation_id=evaluation_id if evaluation_id else None,
            expected_text=expected_text,
            spoken_text=spoken_text,
            comparison_data=comparison_result,
            accuracy_score=comparison_result['accuracy_score'],
            matched_words=comparison_result['matched_words'],
            total_words=comparison_result['total_words']
        )
        
        # Save audio file
        from django.core.files.base import ContentFile
        with open(temp_path, 'rb') as f:
            practice.audio_file.save(f'practice_{practice.id}.wav', ContentFile(f.read()))
        
        return Response({
            'success': True,
            'practice_id': practice.id,
            'spoken_text': spoken_text,
            'comparison': comparison_result['comparison'],
            'accuracy_score': comparison_result['accuracy_score'],
            'matched_words': comparison_result['matched_words'],
            'total_words': comparison_result['total_words']
        })
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@login_required
def app_recommendations_view(request, evaluation_id):
    """Show recommended apps for improvement"""
    from django.http import Http404
    
    try:
        evaluation = VoiceEvaluation.objects.get(pk=evaluation_id, user=request.user)
    except VoiceEvaluation.DoesNotExist:
        raise Http404("Evaluation not found")
    
    # Get recommendations
    level = evaluation.estimated_level or 'B1'
    language = evaluation.language
    recommendations = pronunciation_service.get_app_recommendations(level, language)
    
    context = {
        'evaluation': evaluation,
        'recommendations': recommendations,
        'level': level
    }
    return render(request, 'voice_eval/app_recommendations.html', context)


@login_required
def sound_practice_view(request):
    """Sound practice exercises"""
    language = request.GET.get('language', 'en')
    
    # Sound practice exercises
    exercises = {
        'en': [
            {'sound': 'TH /θ/', 'words': ['think', 'thank', 'through', 'thought'], 
             'sentence': 'I think three things through thoroughly.'},
            {'sound': 'R /r/', 'words': ['red', 'run', 'river', 'right'], 
             'sentence': 'The red rabbit ran rapidly around the river.'},
            {'sound': 'L /l/', 'words': ['light', 'leave', 'little', 'love'], 
             'sentence': 'Little Lucy loves the lovely light.'},
            {'sound': 'V /v/', 'words': ['very', 'voice', 'value', 'view'], 
             'sentence': 'The very valuable vase has a beautiful view.'},
            {'sound': 'W /w/', 'words': ['we', 'will', 'why', 'way'], 
             'sentence': 'Why will we wait when we know the way?'}
        ],
        'fr': [
            {'sound': 'R /ʁ/', 'words': ['rouge', 'rue', 'rire', 'roi'], 
             'sentence': 'Le roi rouge rit dans la rue.'},
            {'sound': 'U /y/', 'words': ['tu', 'rue', 'sûr', 'pur'], 
             'sentence': 'Tu es sûr de trouver la rue pure.'},
            {'sound': 'ON /ɔ̃/', 'words': ['bon', 'mon', 'son', 'pont'], 
             'sentence': 'Mon bon son sur le pont.'},
            {'sound': 'AN /ɑ̃/', 'words': ['dans', 'grand', 'blanc', 'chant'], 
             'sentence': 'Dans le grand chant blanc.'},
            {'sound': 'OI /wa/', 'words': ['moi', 'toi', 'roi', 'voix'], 
             'sentence': 'Moi et toi avec le roi et sa voix.'}
        ]
    }
    
    context = {
        'exercises': exercises.get(language, exercises['en']),
        'language': language
    }
    return render(request, 'voice_eval/sound_practice.html', context)

