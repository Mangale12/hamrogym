from datetime import datetime, timedelta

from django import forms
from django.db.models import Q

from ..models import ClassRoom, ClassSchedule, GymClass, Trainer


def _include_current(base_queryset, current_id):
    if current_id:
        return base_queryset.model.objects.filter(Q(pk=current_id) | Q(pk__in=base_queryset.values("pk")))
    return base_queryset


class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = [
            "gym_class",
            "class_room",
            "trainer",
            "day_of_week",
            "start_time",
            "end_time",
            "is_active",
            "remarks",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["end_time"].required = False

        selected_gym_class_id = self.data.get("gym_class") if self.is_bound else getattr(self.instance, "gym_class_id", None)
        selected_room_id = self.data.get("class_room") if self.is_bound else getattr(self.instance, "class_room_id", None)
        selected_trainer_id = self.data.get("trainer") if self.is_bound else getattr(self.instance, "trainer_id", None)

        class_queryset = GymClass.objects.filter(is_active=True)
        class_queryset = _include_current(class_queryset, selected_gym_class_id)
        self.fields["gym_class"].queryset = class_queryset.order_by("name")

        room_queryset = ClassRoom.objects.filter(is_active=True)
        room_queryset = _include_current(room_queryset, selected_room_id)
        self.fields["class_room"].queryset = room_queryset.order_by("name")

        trainer_queryset = Trainer.objects.filter(status=Trainer.Status.ACTIVE)
        trainer_queryset = _include_current(trainer_queryset, selected_trainer_id)
        self.fields["trainer"].queryset = trainer_queryset.order_by("employee__employee_id")

    def clean(self):
        cleaned_data = super().clean()
        gym_class = cleaned_data.get("gym_class")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if gym_class and start_time and (end_time is None or end_time <= start_time):
            duration_minutes = getattr(gym_class, "duration_minutes", None) or 0
            if duration_minutes > 0:
                computed_end = (
                    datetime.combine(datetime.today(), start_time) + timedelta(minutes=duration_minutes)
                ).time()
                cleaned_data["end_time"] = computed_end
                self.instance.end_time = computed_end

        return cleaned_data
