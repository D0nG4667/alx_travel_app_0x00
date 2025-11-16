#!/usr/bin/env python3
"""Seed the database with sample listings, bookings, and reviews for development and testing."""

from __future__ import annotations

import random
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Review
from django.contrib.auth.models import AbstractUser

User = get_user_model()

SAMPLE_LISTINGS = [
    {
        'title': 'Cozy studio near downtown',
        'description': 'Compact, clean studio perfect for solo travelers.',
        'location': 'Downtown',
        'price_per_night': Decimal('35.00'),
        'max_guests': 2,
    },
    {
        'title': 'Spacious 2BR apartment',
        'description': 'Two bedroom apartment with kitchen and balcony.',
        'location': 'Uptown',
        'price_per_night': Decimal('85.00'),
        'max_guests': 4,
    },
    {
        'title': 'Countryside cottage',
        'description': 'Peaceful cottage with a garden and river views.',
        'location': 'Countryside',
        'price_per_night': Decimal('60.00'),
        'max_guests': 3,
    },
]

AMENITIES_POOL = ['WiFi', 'Air Conditioning', 'Kitchen', 'Parking', 'Washer', 'Heating']


class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=3, help='Number of listings to create'
        )
        parser.add_argument(
            '--reviews', type=int, default=1, help='Reviews per listing'
        )
        parser.add_argument(
            '--bookings', type=int, default=1, help='Bookings per listing'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options['count']
        review_count = options['reviews']
        booking_count = options['bookings']

        self.stdout.write('🔧 Seeding database...')

        host = self._get_or_create_user('host_user', 'host@example.com')
        guest = self._get_or_create_user('guest_user', 'guest@example.com')

        for i, data in enumerate(SAMPLE_LISTINGS[:count], start=1):
            listing = Listing.objects.create(
                host=host,
                title=data['title'],
                description=data['description'],
                location=data['location'],
                price_per_night=data['price_per_night'],
                max_guests=data['max_guests'],
                amenities=random.sample(AMENITIES_POOL, k=random.randint(2, 4)),
                available=True,
            )
            self.stdout.write(f'✅ Created listing: {listing.title}')

            self._create_bookings(listing, guest, booking_count, offset=i)
            self._create_reviews(listing, guest, review_count)

        self.stdout.write(self.style.SUCCESS('🎉 Seeding complete.'))

    def _get_or_create_user(self, username: str, email: str) -> AbstractUser:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': False},
        )
        if created:
            user.set_password('password')
            user.save()
            self.stdout.write(f'👤 Created user: {username}')
        return user

    def _create_bookings(
        self, listing: Listing, guest: AbstractUser, count: int, offset: int
    ):
        for j in range(count):
            start = date.today() + timedelta(days=offset + j * 3)
            end = start + timedelta(days=2)
            Booking.objects.create(
                listing=listing,
                guest=guest,
                start_date=start,
                end_date=end,
                total_price=listing.price_per_night * Decimal('2.00'),
                status=Booking.STATUS_CONFIRMED,
            )
            self.stdout.write(f'📅 Booking added for {listing.title} ({start} → {end})')

    def _create_reviews(self, listing: Listing, guest: AbstractUser, count: int):
        for k in range(count):
            Review.objects.update_or_create(
                listing=listing,
                user=guest,
                defaults={
                    'rating': random.randint(3, 5),
                    'comment': random.choice(
                        [
                            'Great place!',
                            'Very clean and cozy.',
                            'Would stay again.',
                            'Loved the location!',
                        ]
                    ),
                },
            )
            self.stdout.write(f'⭐ Review added for {listing.title}')
