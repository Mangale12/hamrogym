from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from core.choices import MODULE_CHOICES


class Policy(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    module = models.CharField(max_length=255, choices=MODULE_CHOICES)
    trigger_event = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional event name like check_in or check_out.",
    )
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=1)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["priority", "name"]
        verbose_name = "Policy"
        verbose_name_plural = "Policies"

    def __str__(self) -> str:
        return self.name


class PolicyCondition(models.Model):
    FIELD_EMPLOYEE = "employee_id"
    FIELD_DEPARTMENT = "department_id"
    FIELD_DESIGNATION = "designation_id"
    FIELD_EMPLOYEE_TYPE = "employee_type"
    FIELD_EMPLOYMENT_STATUS = "employment_status"
    FIELD_SHIFT = "shift_id"
    FIELD_SHIFT_CODE = "shift_code"
    FIELD_ATTENDANCE_STATUS = "attendance_status"
    FIELD_CHECK_IN_TIME = "check_in_time"
    FIELD_CHECK_OUT_TIME = "check_out_time"
    FIELD_IS_LATE = "is_late"
    FIELD_IS_HALF_DAY = "is_half_day"
    FIELD_WEEKDAY = "weekday"
    FIELD_OVERTIME_DATE = "overtime_date"
    FIELD_OVERTIME_START_TIME = "overtime_start_time"
    FIELD_OVERTIME_END_TIME = "overtime_end_time"
    FIELD_OVERTIME_STATUS = "overtime_status"
    FIELD_REQUESTED_HOURS = "requested_hours"
    FIELD_OVERTIME_HOURS = "overtime_hours"
    FIELD_OVERTIME_RATE = "overtime_rate"
    FIELD_OVERTIME_AMOUNT = "overtime_amount"
    FIELD_CHOICES = [
        (FIELD_EMPLOYEE, "Employee"),
        (FIELD_DEPARTMENT, "Department"),
        (FIELD_DESIGNATION, "Designation"),
        (FIELD_EMPLOYEE_TYPE, "Employee Type"),
        (FIELD_EMPLOYMENT_STATUS, "Employment Status"),
        (FIELD_SHIFT, "Shift"),
        (FIELD_SHIFT_CODE, "Shift Code"),
        (FIELD_ATTENDANCE_STATUS, "Attendance Status"),
        (FIELD_CHECK_IN_TIME, "Check In Time"),
        (FIELD_CHECK_OUT_TIME, "Check Out Time"),
        (FIELD_IS_LATE, "Is Late"),
        (FIELD_IS_HALF_DAY, "Is Half Day"),
        (FIELD_WEEKDAY, "Weekday"),
        (FIELD_OVERTIME_DATE, "Overtime Date"),
        (FIELD_OVERTIME_START_TIME, "Overtime Start Time"),
        (FIELD_OVERTIME_END_TIME, "Overtime End Time"),
        (FIELD_OVERTIME_STATUS, "Overtime Status"),
        (FIELD_REQUESTED_HOURS, "Requested Hours"),
        (FIELD_OVERTIME_HOURS, "Overtime Hours"),
        (FIELD_OVERTIME_RATE, "Overtime Rate"),
        (FIELD_OVERTIME_AMOUNT, "Overtime Amount"),
    ]

    OPERATOR_EQ = "eq"
    OPERATOR_NEQ = "neq"
    OPERATOR_GT = "gt"
    OPERATOR_GTE = "gte"
    OPERATOR_LT = "lt"
    OPERATOR_LTE = "lte"
    OPERATOR_IN = "in"
    OPERATOR_NOT_IN = "not_in"
    OPERATOR_CONTAINS = "contains"
    OPERATOR_IS_TRUE = "is_true"
    OPERATOR_IS_FALSE = "is_false"
    OPERATOR_IS_NULL = "is_null"
    OPERATOR_NOT_NULL = "not_null"
    OPERATOR_CHOICES = [
        (OPERATOR_EQ, "Equals"),
        (OPERATOR_NEQ, "Not Equals"),
        (OPERATOR_GT, "Greater Than"),
        (OPERATOR_GTE, "Greater Than or Equal"),
        (OPERATOR_LT, "Less Than"),
        (OPERATOR_LTE, "Less Than or Equal"),
        (OPERATOR_IN, "In"),
        (OPERATOR_NOT_IN, "Not In"),
        (OPERATOR_CONTAINS, "Contains"),
        (OPERATOR_IS_TRUE, "Is True"),
        (OPERATOR_IS_FALSE, "Is False"),
        (OPERATOR_IS_NULL, "Is Null"),
        (OPERATOR_NOT_NULL, "Is Not Null"),
    ]

    LOGICAL_AND = "AND"
    LOGICAL_OR = "OR"
    LOGICAL_OPERATOR_CHOICES = [
        (LOGICAL_AND, "AND"),
        (LOGICAL_OR, "OR"),
    ]

    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="conditions")
    field_name = models.CharField(max_length=255, choices=FIELD_CHOICES)
    operator = models.CharField(max_length=255, choices=OPERATOR_CHOICES, default=OPERATOR_EQ)
    value = models.TextField(blank=True)
    logical_operator = models.CharField(
        max_length=10,
        choices=LOGICAL_OPERATOR_CHOICES,
        default=LOGICAL_AND,
    )
    sequence = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["policy", "sequence", "id"]
        verbose_name = "Policy Condition"
        verbose_name_plural = "Policy Conditions"

    def __str__(self) -> str:
        return f"{self.policy.name} - {self.field_name} {self.operator}".strip()


class PolicyAction(models.Model):
    ACTION_SET_FIELD = "SET_FIELD"
    ACTION_APPEND_REMARK = "APPEND_REMARK"
    ACTION_MARK_LATE = "MARK_LATE"
    ACTION_MARK_HALF_DAY = "MARK_HALF_DAY"
    ACTION_SET_STATUS = "SET_STATUS"
    ACTION_CHOICES = [
        (ACTION_SET_FIELD, "Set field"),
        (ACTION_APPEND_REMARK, "Append remark"),
        (ACTION_MARK_LATE, "Mark late"),
        (ACTION_MARK_HALF_DAY, "Mark half day"),
        (ACTION_SET_STATUS, "Set status"),
    ]
    TARGET_FIELD_STATUS = "status"
    TARGET_FIELD_REMARKS = "remarks"
    TARGET_FIELD_IS_LATE = "is_late"
    TARGET_FIELD_IS_HALF_DAY = "is_half_day"
    TARGET_FIELD_CHOICES = [
        (TARGET_FIELD_STATUS, "Status"),
        (TARGET_FIELD_REMARKS, "Remarks"),
        (TARGET_FIELD_IS_LATE, "Is Late"),
        (TARGET_FIELD_IS_HALF_DAY, "Is Half Day"),
    ]

    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES, default=ACTION_SET_FIELD)
    target_field = models.CharField(max_length=255, blank=True, choices=TARGET_FIELD_CHOICES)
    action_value = models.TextField(blank=True)
    sequence = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["policy", "sequence", "id"]
        verbose_name = "Policy Action"
        verbose_name_plural = "Policy Actions"

    def __str__(self) -> str:
        label = self.target_field or self.action_type
        return f"{self.policy.name} - {label}"


class PolicyScope(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="scopes")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    scope_object = GenericForeignKey("content_type", "object_id")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["policy", "content_type", "object_id"]
        verbose_name = "Policy Scope"
        verbose_name_plural = "Policy Scopes"
        unique_together = [("policy", "content_type", "object_id")]

    def __str__(self) -> str:
        return f"{self.policy.name} - {self.scope_object or self.content_type}"
