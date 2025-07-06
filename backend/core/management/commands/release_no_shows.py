from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import date,time,datetime
from core.models import Booking,Waitlist,Seat

class Command(BaseCommand):
    help = 'Cancel bookings for users who did not mark attendance by cutoff time and promote waitlisted users'

    def handle(self, *args , **kwargs):
        today = date.today()
        cutoff_time = time(0,0) # 10 AM
        current_time = now().time()

        if current_time < cutoff_time:
            self.stdout.write('Cutoff time not reached yet.')
            return

        # no-show bookings for today
        no_show_booking = Booking.objects.filter(
            date = today,
            marked_attendance = False
        )

        count = 0
        for booking in no_show_booking:
            seat = booking.seat
            user = booking.user
            booking.delete()
            count += 1
            self.stdout.write(f"Cancelled booking for {user} at seat {seat.label}")

            # next user from waitlist is promoted
            next_in_line = Waitlist.objects.filter(seat = seat , date=today).order_by('joined_at').first()

            if next_in_line:
                Booking.objects.create(
                    user = next_in_line.user,
                    seat = seat,
                    date = today
                )

                self.stdout.write(f"Promoted waitlisted user {next_in_line.user} to seat {seat.label}")
                next_in_line.delete()

        self.stdout.write(self.style.SUCCESS(f"Released {count} no-show bookings."))
        