class APSchedulerJobConfig(object):
    SCHEDULER_API_ENABLED = True
    JOBS = [
        {
            "id": "No1",
            "func": "functions:get_daily_news",
            "trigger": {
                "type": "interval",
                # "day_of_week": "0-6",
                 #"hour": "12",
                # "minute": "1",
                "seconds": 3000,
            },
        }
    ]
