import datetime

from django.utils.dateparse import parse_datetime, parse_time
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from food_menus.models import MenuModel
from .models import RestaurantModel, TableModel, ReservationModel
from .forms import CreateRestaurantForm, CreateTableForm


# TODO:
# - add authentication for all views (@login_required)
# - authenticate resturant admin
# - check all views work fine


def index_view(request):
    food_menus = MenuModel.objects.all()[:10]
    return render(request, "pages/index.html", {"food_menus": food_menus})


# FIXME: get and clean data from form
def create_restaurant_view(request):
    if request.method == "POST":
        form = CreateRestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.save()
            messages.success(request, "A new Restaurant is created successfully")
            # TODO: redirect to restaurant's table list page
            return redirect("/")
    else:
        form = CreateRestaurantForm()
    return render(request, "reservation/create_restaurant.html", {"form": form})


# FIXME: review and fixme later
def update_resturant_view(request, id):
    restaurant = get_object_or_404(RestaurantModel, id=id)
    if request.method == "POST":
        form = CreateRestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.save()
            messages.success(
                request, "Restaurant's informations are updated successfully"
            )
            # TODO: redirect to restaurant's update page
            return redirect("/")
    else:
        form = CreateRestaurantForm(instance=restaurant)
    return render(request, "reservation/update_restaurant.html", {"form": form})


# FIXME: review later
def add_table_view(request, restaurant_id):
    restaurant = get_object_or_404(RestaurantModel, id=restaurant_id)
    if request.method == "POST":
        form = CreateTableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.restaurant = restaurant
            table.save()
            messages.success(request, "Table created successfully")
            # TODO: redirect to restaurant's table list page
            return redirect("/")
    else:
        form = CreateTableForm()

    context = {
        "form": form,
        "restaurant": restaurant,
    }
    return render(request, "reservation/add_table.html", context=context)


# FIXME: review later
def update_table_view(request, table_id):
    table = get_object_or_404(TableModel, id=table_id)
    if request.method == "POST":
        form = CreateTableForm(request.POST, instance=table)
        if form.is_valid():
            table = form.save(commit=False)
            table.save()
            messages.success(request, "Table's informations are updated successfully")
            # TODO: redirect to table upadate page
            return redirect("/")
    else:
        form = CreateTableForm(instance=table)
    return render(request, "reservation/update_table.html", {"form": form})


# FIXME: Review later
def delete_table_view(request, table_id):
    table = get_object_or_404(TableModel, id=table_id)
    table.delete()
    messages.success(request, "Table is deleted successfully")
    return redirect("/")


def make_reservation_view(request):
    tables = TableModel.objects.all()
    times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    if request.method == "POST":
        date = request.POST["date"]
        time = request.POST["time"]
        table_code = request.POST["table_size"]

        customer = request.user
        table = TableModel.objects.filter(table_number=table_code).first()
        parsed_date = datetime.datetime.strptime(date, "%m/%d/%Y").date()
        parsed_time = parse_time(time)

        if parsed_date >= timezone.now().date():
            if ReservationModel.objects.filter(
                customer=customer,
                table=table,
                reservation_date=parsed_date,
                reservation_time=parsed_time,
            ).exists():
                messages.error(
                    request, "This table is already reserved for the date or time."
                )
                return redirect("make_reservation")
            else:
                reservation = ReservationModel.objects.create(
                    customer=customer,
                    table=table,
                    reservation_date=parsed_date,
                    reservation_time=parsed_time,
                )
                reservation.save()
                return render(
                    request,
                    "reservation/confirm.html",
                    {"date": date, "time": time, "table": table_code},
                )
        else:
            messages.error(request, "You can't reserve a table in the past!")
            return redirect("make_reservation")

    else:
        return render(
            request,
            "reservation/make_reservation.html",
            {"tables": tables, "available_times": times},
        )


# FIXME: get and clean data from form for update view
def update_reservation_view(request, reservation_id):
    reservation = get_object_or_404(ReservationModel, id=reservation_id)
    if request.method == "POST":
        reservation.start_time = parse_datetime(request.POST["start_time"])
        reservation.end_time = parse_datetime(request.POST["end_time"])
        reservation.save()
        messages.success(request, "Reservation is updated successfully")
        return redirect("/")
    else:
        return render(
            request, "reservation/update_reservation.html", {"reservation": reservation}
        )


# TODO: write delete view
def delete_reservation_view(request, reservation_id):
    pass


# TODO: test this view later
def check_duplicate_reservation(request, table_id):
    table = get_object_or_404(TableModel, id=table_id)
    if request.method == "POST":
        start_time = parse_datetime(request.POST["start_time"])
        end_time = parse_datetime(request.POST["end_time"])
        if ReservationModel.objects.filter(
            table=table, start_time__gte=start_time, end_time__lte=end_time
        ).exists():
            return render(
                request,
                "reservation/check_duplicate_reservation.html",
                {"table": table},
            )
        else:
            return redirect("/")
    else:
        return render(
            request, "reservation/duplicate_reservation.html", {"table": table}
        )
