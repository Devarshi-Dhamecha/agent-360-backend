from django.db import models


class UserRole(models.Model):
    """Salesforce UserRole mapping - defines organizational hierarchy roles"""
    ur_sf_id = models.CharField(
        max_length=18, 
        primary_key=True, 
        db_column='ur_sf_id',
        verbose_name='Salesforce ID'
    )
    ur_name = models.CharField(
        max_length=80, 
        db_column='ur_name',
        verbose_name='Role Name'
    )
    ur_last_modified_date = models.DateTimeField(
        db_column='ur_last_modified_date',
        verbose_name='Last Modified Date'
    )
    ur_system_modstamp = models.DateTimeField(
        db_column='ur_system_modstamp',
        verbose_name='System Modstamp'
    )
    ur_active = models.SmallIntegerField(
        default=1, 
        db_column='ur_active',
        verbose_name='Active Flag'
    )
    ur_created_at = models.DateTimeField(
        auto_now_add=True, 
        db_column='ur_created_at',
        verbose_name='Created At'
    )
    ur_updated_at = models.DateTimeField(
        auto_now=True, 
        db_column='ur_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'user_roles'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        indexes = [
            models.Index(fields=['ur_active'], name='idx_user_roles_active'),
        ]

    def __str__(self):
        return self.ur_name


class User(models.Model):
    """Salesforce User - represents system users and sales representatives"""
    usr_sf_id = models.CharField(
        max_length=18, 
        primary_key=True, 
        db_column='usr_sf_id',
        verbose_name='Salesforce ID'
    )
    usr_username = models.CharField(
        max_length=80, 
        db_column='usr_username',
        verbose_name='Username'
    )
    usr_email = models.EmailField(
        max_length=255, 
        db_column='usr_email',
        verbose_name='Email'
    )
    usr_first_name = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        db_column='usr_first_name',
        verbose_name='First Name'
    )
    usr_last_name = models.CharField(
        max_length=255, 
        db_column='usr_last_name',
        verbose_name='Last Name'
    )
    usr_name = models.CharField(
        max_length=255, 
        db_column='usr_name',
        verbose_name='Full Name'
    )
    usr_is_active = models.BooleanField(
        db_column='usr_is_active',
        verbose_name='Is Active'
    )
    usr_profile_id = models.CharField(
        max_length=18, 
        null=True, 
        blank=True, 
        db_column='usr_profile_id',
        verbose_name='Profile ID'
    )
    usr_user_role_id = models.ForeignKey(
        'users.UserRole',
        to_field='ur_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='usr_user_role_id',
        verbose_name='User Role'
    )
    usr_federation_id = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        db_column='usr_federation_id',
        verbose_name='Federation ID'
    )
    usr_time_zone = models.CharField(
        max_length=100, 
        db_column='usr_time_zone',
        verbose_name='Time Zone'
    )
    usr_language = models.CharField(
        max_length=100, 
        db_column='usr_language',
        verbose_name='Language'
    )
    usr_sf_created_date = models.DateTimeField(
        db_column='usr_sf_created_date',
        verbose_name='SF Created Date'
    )
    usr_last_modified_date = models.DateTimeField(
        db_column='usr_last_modified_date',
        verbose_name='Last Modified Date'
    )
    usr_last_modified_by_id = models.CharField(
        max_length=18, 
        db_column='usr_last_modified_by_id',
        verbose_name='Last Modified By ID'
    )
    usr_active = models.SmallIntegerField(
        default=1, 
        db_column='usr_active',
        verbose_name='Active Flag'
    )
    usr_created_at = models.DateTimeField(
        auto_now_add=True, 
        db_column='usr_created_at',
        verbose_name='Created At'
    )
    usr_updated_at = models.DateTimeField(
        auto_now=True, 
        db_column='usr_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['usr_email'], name='idx_users_email'),
            models.Index(fields=['usr_active'], name='idx_users_active'),
            models.Index(fields=['usr_federation_id'], name='idx_users_federation_id'),
        ]

    def __str__(self):
        return self.usr_name


class RecordType(models.Model):
    """Salesforce RecordType - defines different record types for objects"""
    rt_sf_id = models.CharField(
        max_length=18, 
        primary_key=True, 
        db_column='rt_sf_id',
        verbose_name='Salesforce ID'
    )
    rt_name = models.CharField(
        max_length=80, 
        db_column='rt_name',
        verbose_name='Name'
    )
    rt_developer_name = models.CharField(
        max_length=80, 
        db_column='rt_developer_name',
        verbose_name='Developer Name'
    )
    rt_sobject_type = models.CharField(
        max_length=40, 
        db_column='rt_sobject_type',
        verbose_name='SObject Type'
    )
    rt_is_active = models.BooleanField(
        db_column='rt_is_active',
        verbose_name='Is Active'
    )
    rt_sf_created_date = models.DateTimeField(
        db_column='rt_sf_created_date',
        verbose_name='SF Created Date'
    )
    rt_last_modified_date = models.DateTimeField(
        db_column='rt_last_modified_date',
        verbose_name='Last Modified Date'
    )
    rt_last_modified_by_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='rt_last_modified_by_id',
        verbose_name='Last Modified By'
    )
    rt_active = models.SmallIntegerField(
        default=1, 
        db_column='rt_active',
        verbose_name='Active Flag'
    )
    rt_created_at = models.DateTimeField(
        auto_now_add=True, 
        db_column='rt_created_at',
        verbose_name='Created At'
    )
    rt_updated_at = models.DateTimeField(
        auto_now=True, 
        db_column='rt_updated_at',
        verbose_name='Updated At'
    )

    class Meta:
        db_table = 'record_types'
        verbose_name = 'Record Type'
        verbose_name_plural = 'Record Types'
        indexes = [
            models.Index(fields=['rt_sobject_type'], name='idx_record_types_sobject'),
        ]

    def __str__(self):
        return f"{self.rt_name} ({self.rt_sobject_type})"


class UserLoginLog(models.Model):
    """Tracks user login sessions and activity"""
    ull_id = models.AutoField(
        primary_key=True, 
        db_column='ull_id',
        verbose_name='ID'
    )
    ull_user_sf_id = models.ForeignKey(
        'users.User',
        to_field='usr_sf_id',
        on_delete=models.CASCADE,
        db_column='ull_user_sf_id',
        verbose_name='User'
    )
    ull_login_at = models.DateTimeField(
        auto_now_add=True, 
        db_column='ull_login_at',
        verbose_name='Login At'
    )
    ull_ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True, 
        db_column='ull_ip_address',
        verbose_name='IP Address'
    )
    ull_user_agent = models.CharField(
        max_length=500, 
        null=True, 
        blank=True, 
        db_column='ull_user_agent',
        verbose_name='User Agent'
    )
    ull_session_duration_sec = models.IntegerField(
        null=True, 
        blank=True, 
        db_column='ull_session_duration_sec',
        verbose_name='Session Duration (sec)'
    )
    ull_logout_at = models.DateTimeField(
        null=True, 
        blank=True, 
        db_column='ull_logout_at',
        verbose_name='Logout At'
    )

    class Meta:
        db_table = 'user_login_log'
        verbose_name = 'User Login Log'
        verbose_name_plural = 'User Login Logs'
        indexes = [
            models.Index(fields=['ull_user_sf_id'], name='idx_user_login_log_user'),
            models.Index(fields=['ull_login_at'], name='idx_user_login_log_login_at'),
        ]

    def __str__(self):
        return f"Login: {self.ull_user_sf_id} at {self.ull_login_at}"
