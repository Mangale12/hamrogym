from django import forms

from .workout_plan_form import _apply_bootstrap_widgets
from ..models import (
    AchievementBadge,
    Challenge,
    ChallengeParticipant,
    ChallengeProgressLog,
    Leaderboard,
    MemberBadge,
    MemberReward,
    MemberStreak,
    Reward,
)


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = [
            "title",
            "description",
            "challenge_type",
            "goal_target",
            "goal_unit",
            "start_date",
            "end_date",
            "participation_type",
            "visibility",
            "branch",
            "status",
            "remarks",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "goal_target": forms.NumberInput(attrs={"min": 0.01, "step": "0.01"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["branch"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class ChallengeParticipantForm(forms.ModelForm):
    class Meta:
        model = ChallengeParticipant
        fields = [
            "challenge",
            "member",
            "joined_at",
            "current_progress",
            "completion_percentage",
            "current_rank",
            "status",
            "remarks",
        ]
        widgets = {
            "joined_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "current_progress": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "completion_percentage": forms.NumberInput(attrs={"min": 0, "max": 100, "step": "0.01"}),
            "current_rank": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["current_rank"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class ChallengeProgressLogForm(forms.ModelForm):
    class Meta:
        model = ChallengeProgressLog
        fields = [
            "challenge_participant",
            "logged_at",
            "progress_value",
            "source_type",
            "notes",
            "remarks",
        ]
        widgets = {
            "logged_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "progress_value": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class LeaderboardForm(forms.ModelForm):
    class Meta:
        model = Leaderboard
        fields = [
            "challenge",
            "generated_at",
            "member",
            "rank_position",
            "score_value",
            "remarks",
        ]
        widgets = {
            "generated_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "rank_position": forms.NumberInput(attrs={"min": 1}),
            "score_value": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class AchievementBadgeForm(forms.ModelForm):
    class Meta:
        model = AchievementBadge
        fields = [
            "name",
            "description",
            "icon",
            "badge_type",
            "criteria_value",
            "status",
            "remarks",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "criteria_value": forms.NumberInput(attrs={"min": 0.01, "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["icon"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class MemberBadgeForm(forms.ModelForm):
    class Meta:
        model = MemberBadge
        fields = [
            "member",
            "achievement_badge",
            "awarded_at",
            "source_reference_type",
            "source_reference_id",
            "remarks",
        ]
        widgets = {
            "awarded_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "source_reference_id": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source_reference_type"].required = False
        self.fields["source_reference_id"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class MemberStreakForm(forms.ModelForm):
    class Meta:
        model = MemberStreak
        fields = [
            "member",
            "streak_type",
            "current_streak",
            "longest_streak",
            "last_activity_date",
            "remarks",
        ]
        widgets = {
            "current_streak": forms.NumberInput(attrs={"min": 0}),
            "longest_streak": forms.NumberInput(attrs={"min": 0}),
            "last_activity_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["last_activity_date"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = [
            "name",
            "reward_type",
            "description",
            "points_required",
            "status",
            "remarks",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "points_required": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["points_required"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class MemberRewardForm(forms.ModelForm):
    class Meta:
        model = MemberReward
        fields = [
            "member",
            "reward",
            "redeemed_at",
            "status",
            "remarks",
        ]
        widgets = {
            "redeemed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)
