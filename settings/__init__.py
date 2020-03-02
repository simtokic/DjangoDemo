from split_settings.tools import optional, include

include(
    'components/base.py',
    'components/database.py',
    'components/admin.py',
    'components/email.py',
    'components/misc.py',
    # Local settings, overrides settings above, not in VCS
    optional('components/local_settings.py')
)
