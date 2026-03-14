# reception/config.py
from hotel_app.reception.views import (
    guest_view,
    booking_view,
    checkin_view,
    check_out_view,
)

from hotel_app.reception.datatables.guest_data_table import GuestDataTable
from hotel_app.reception.datatables.booking_data_table import BookingDataTable
from hotel_app.reception.datatables.checkin_data_table import CheckInDataTable
from hotel_app.reception.datatables.check_out_data_table import CheckOutDataTable

# Define all your CRUD entities in one place
RECEPTION_ENTITIES = [
    {
        'name': 'guest',
        'view_module': guest_view,
        'datatable_view': GuestDataTable,
        'verbose_name': 'Guest'
    },
    {
        'name': 'booking',
        'view_module': booking_view,
        'datatable_view': BookingDataTable,
        'verbose_name': 'Booking'
    },
    {
        'name': 'checkin',
        'view_module': checkin_view,
        'datatable_view': CheckInDataTable,
        'verbose_name': 'Checkin'
    },
    {
        'name': 'check_out',
        'view_module': check_out_view,
        'datatable_view': CheckOutDataTable,
        'verbose_name': 'Check Out'
    },
]