from django.urls import path
from core.views.user_views import register_user,login_user
from core.views.seat_views import get_seats_by_floorplan
from core.views.booking_views import create_booking,mark_attendance,cancel_booking
from core.views.floorplan_views import list_floorplans,create_floorplan
from core.views.analytics_views import booking_summary
from core.views.waitlist_views import join_waitlist,my_waitlist,leave_waitlist

urlpatterns = [
    path('auth/register/', register_user),
    path('auth/login/',login_user),
    path('seats/',get_seats_by_floorplan),
    path('bookings/',create_booking),
    path('bookings/mark/',mark_attendance),
    path('floorplans/',list_floorplans),
    path('floorplans/create/',create_floorplan),
    path('analytics/summary/',booking_summary),
    path('waitlist/join/',join_waitlist),
    path('waitlist/my/',my_waitlist),
    path('waitlist/leave/<int:waitlist_id>/',leave_waitlist),
    path('bookings/cancel/<int:booking_id>',cancel_booking)

]