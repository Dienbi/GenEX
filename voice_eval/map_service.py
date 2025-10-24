"""Service for generating maps with testing center locations"""
import folium
from folium import plugins
from django.conf import settings


class TestingCenterMapService:
    """Generate interactive maps showing language testing centers"""
    
    def generate_map(self, centers, user_location=None):
        """
        Generate an interactive map with testing centers
        
        Args:
            centers: QuerySet or list of TestingCenter objects
            user_location: Optional tuple (latitude, longitude) for user's location
            
        Returns:
            HTML string of the folium map
        """
        # Default center (Tunisia - ESPRIT location)
        if user_location:
            map_center = user_location
            zoom = 12
        elif centers:
            # Center on first testing center
            map_center = [centers[0].latitude, centers[0].longitude]
            zoom = 10
        else:
            # Default to Tunis, Tunisia
            map_center = [36.8065, 10.1815]
            zoom = 12
        
        # Create map
        m = folium.Map(
            location=map_center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # Add user location if provided
        if user_location:
            folium.Marker(
                user_location,
                popup="Your Location",
                tooltip="You are here",
                icon=folium.Icon(color='blue', icon='user', prefix='fa')
            ).add_to(m)
        
        # Add testing centers with red markers
        for center in centers:
            # Format languages nicely
            lang_display = ', '.join(['🇬🇧 English' if lang == 'en' else '🇫🇷 French' for lang in center.languages])
            
            # Create popup content with enhanced styling
            popup_html = f"""
            <div style="width: 280px; font-family: Arial, sans-serif; padding: 5px;">
                <h3 style="margin: 0 0 12px 0; color: #dc3545; border-bottom: 2px solid #dc3545; padding-bottom: 8px;">
                    <i class="fas fa-map-marker-alt"></i> {center.name}
                </h3>
                <p style="margin: 8px 0; font-size: 14px;">
                    <i class="fas fa-map-pin" style="color: #dc3545; width: 20px;"></i>
                    <strong>Address:</strong><br>
                    <span style="margin-left: 24px;">{center.address}<br>{center.city}, {center.country}</span>
                </p>
                {'<p style="margin: 8px 0; font-size: 14px;"><i class="fas fa-phone" style="color: #28a745; width: 20px;"></i> <strong>Phone:</strong> ' + center.phone + '</p>' if center.phone else ''}
                {'<p style="margin: 8px 0; font-size: 14px;"><i class="fas fa-envelope" style="color: #17a2b8; width: 20px;"></i> <strong>Email:</strong> ' + center.email + '</p>' if center.email else ''}
                {'<p style="margin: 8px 0; font-size: 14px;"><i class="fas fa-globe" style="color: #6c757d; width: 20px;"></i> <strong>Website:</strong> <a href="' + center.website + '" target="_blank" style="color: #007bff;">Visit Site</a></p>' if center.website else ''}
                <p style="margin: 8px 0; font-size: 14px;">
                    <i class="fas fa-language" style="color: #fd7e14; width: 20px;"></i>
                    <strong>Languages:</strong> {lang_display}
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <i class="fas fa-certificate" style="color: #ffc107; width: 20px;"></i>
                    <strong>Certifications:</strong><br>
                    <span style="margin-left: 24px;">{'<br>'.join(['• ' + cert for cert in center.certifications])}</span>
                </p>
            </div>
            """
            
            # Create tooltip with location name and brief info
            tooltip_html = f"""
            <div style="font-family: Arial; font-size: 13px;">
                <strong>{center.name}</strong><br>
                📍 {center.city}<br>
                🗣️ {lang_display}<br>
                <em>Click for details</em>
            </div>
            """
            
            # Add marker with red color and custom icon
            folium.Marker(
                [center.latitude, center.longitude],
                popup=folium.Popup(popup_html, max_width=320),
                tooltip=folium.Tooltip(tooltip_html),
                icon=folium.Icon(
                    color='red',
                    icon='graduation-cap',
                    prefix='fa',
                    icon_color='white'
                )
            ).add_to(m)
        
        # Add marker cluster for better performance with many markers
        if len(centers) > 10:
            marker_cluster = plugins.MarkerCluster().add_to(m)
            
            for center in centers:
                popup_html = f"""
                <div style="width: 250px;">
                    <h4 style="color: #dc3545;">{center.name}</h4>
                    <p><strong>Address:</strong> {center.address}</p>
                    <p><strong>City:</strong> {center.city}</p>
                </div>
                """
                folium.Marker(
                    [center.latitude, center.longitude],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=center.name,
                    icon=folium.Icon(color='red', icon='graduation-cap', prefix='fa')
                ).add_to(marker_cluster)
        
        # Add fullscreen button
        plugins.Fullscreen().add_to(m)
        
        # Add search functionality
        plugins.LocateControl().add_to(m)
        
        # Return HTML
        return m._repr_html_()
    
    def get_nearby_centers(self, centers, user_location, max_distance_km=50):
        """
        Filter centers within a certain distance from user
        
        Args:
            centers: QuerySet or list of TestingCenter objects
            user_location: Tuple (latitude, longitude)
            max_distance_km: Maximum distance in kilometers
            
        Returns:
            List of centers within distance, sorted by distance
        """
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            """Calculate distance between two points on Earth"""
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6371 * c
            return km
        
        user_lat, user_lon = user_location
        nearby = []
        
        for center in centers:
            distance = haversine(user_lon, user_lat, center.longitude, center.latitude)
            if distance <= max_distance_km:
                nearby.append({
                    'center': center,
                    'distance': round(distance, 2)
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance'])
        
        return nearby


# Global instance
map_service = TestingCenterMapService()
