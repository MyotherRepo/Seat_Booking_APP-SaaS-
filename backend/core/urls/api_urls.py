from django.urls import path
from core.views.user_views import register_user,login_user
from core.views.seat_views import get_seats_by_floorplan,seat_grid_status
from core.views.booking_views import create_booking,my_bookings,mark_attendance,cancel_booking
from core.views.floorplan_views import list_floorplans,create_floorplan,bulk_create_seats
from core.views.analytics_views import booking_summary,all_bookings
from core.views.waitlist_views import join_waitlist,my_waitlist,leave_waitlist
from core.views.booking_views import book_seat

urlpatterns = [
    path('auth/register/', register_user),
    path('auth/login/',login_user),
    path('seats/',get_seats_by_floorplan),
    path('bookings/',create_booking),
    path('bookings/my/', my_bookings),
    path('bookings/mark/',mark_attendance),
    path('floorplans/',list_floorplans),
    path('floorplans/create/',create_floorplan),
    path('floorplans/<int:floorplan_id>/seat-grid/', seat_grid_status, name='seat-grid'),
    path('analytics/summary/',booking_summary),
    path('bookings/all/', all_bookings),
    path('waitlist/join/',join_waitlist),
    path('waitlist/my/',my_waitlist),
    path('waitlist/leave/<int:waitlist_id>/',leave_waitlist),
    path('bookings/cancel/<int:booking_id>/',cancel_booking),
    path('book_seat/', book_seat, name='book-seat'),
    path('seats/bulk-create/',bulk_create_seats)

]