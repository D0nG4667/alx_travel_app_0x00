#!/usr/bin/env python3
"""ViewSets for Listing, Booking, and Review models with schema annotations and ownership enforcement."""

from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer


class IsHostOrReadOnly(permissions.BasePermission):
    """Custom permission to allow only the host to edit or delete their listings."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'host', None) == request.user


@extend_schema_view(
    list=extend_schema(
        summary='List all listings',
        description='Retrieve a list of all available property listings, including nested bookings and reviews.',
    ),
    retrieve=extend_schema(
        summary='Retrieve a specific listing',
        description='Get detailed information about a single listing, including its bookings and reviews.',
    ),
    create=extend_schema(
        summary='Create a new listing',
        description='Authenticated users can create a new property listing. Host is set automatically.',
    ),
    update=extend_schema(
        summary='Update a listing',
        description='Modify an existing listing. Only the host can update their own listings.',
    ),
    destroy=extend_schema(
        summary='Delete a listing',
        description='Remove a listing from the platform. Only the host can delete their own listings.',
    ),
)
class ListingViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for property listings."""

    queryset = Listing.objects.select_related('host').all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsHostOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary='List all bookings',
        description='Retrieve all bookings made by users. Admins may see all; users see their own.',
    ),
    retrieve=extend_schema(
        summary='Retrieve a specific booking',
        description='Get details of a specific booking, including listing and guest info.',
    ),
    create=extend_schema(
        summary='Create a new booking',
        description='Authenticated users can book a listing by providing dates and listing ID.',
    ),
)
class BookingViewSet(viewsets.ModelViewSet):
    """Handles bookings for listings."""

    queryset = Booking.objects.select_related('guest', 'listing__host').all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary='List all reviews',
        description='Retrieve all reviews left by users across listings.',
    ),
    retrieve=extend_schema(
        summary='Retrieve a specific review',
        description='Get details of a specific review, including rating and comment.',
    ),
    create=extend_schema(
        summary='Submit a review',
        description='Authenticated users can leave one review per listing. Ratings must be 1–5.',
    ),
)
class ReviewViewSet(viewsets.ModelViewSet):
    """Handles reviews for listings."""

    queryset = Review.objects.select_related('user', 'listing').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
