from __future__ import annotations
from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import sys

from .models import VoiceEvaluation, ReferenceText, VoiceEvaluationHistory

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
from .serializers import (
    VoiceEvaluationSerializer, 
    VoiceEvaluationCreateSerializer,
    VoiceEvaluationDetailSerializer,
    ReferenceTextSerializer,
    VoiceEvaluationHistorySerializer
)
from .ai_service import voice_service


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
    try:
        evaluation = VoiceEvaluation.objects.get(pk=pk, user=request.user)
    except VoiceEvaluation.DoesNotExist:
        from django.http import Http404
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
