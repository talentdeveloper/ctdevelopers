def get_profile_completeness(profile):
    """
    Calculates candidate profile completeness and
    returns data to display progress bar, etc.
    """
    is_complete = False # profile completeness flag for candidate
    progress = 0.3  # profile progress, 0.3 is default after registration
    if (profile.title and profile.city and profile.skills.all() and
        profile.phone and profile.experience and profile.country):
        is_complete = True

    # calculate profile progress in %
    progress += 0.2 if is_complete else 0
    progress += 0.3 if profile.cv else 0
    progress += 0.2 if profile.photo else 0
    progress *= 100

    return {
        'is_complete': is_complete,
        'progress': progress,
        'photo': True if profile.photo else False,
        'cv': True if profile.cv else False,
    }
