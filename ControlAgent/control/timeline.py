def build_timeline_payload(case: int, error: str = "",alertid : str = "No_ID_Input") -> dict:
    """
    Returns a dictionary payload containing timeline stages up to the given case number.
    If `error` is provided, all but the last stage are marked 'success' and the last stage is 'error'.
    If `error` is empty, all stages are marked 'success'.
    """
    if case == 0:
        return {
            "alert_id":alertid,
            "agent.timeline.updated": {
                "data": []
            }
        }

    stage_names = {
        1: 'Received Alert',
        2: 'Type Agent',
        3: 'Analyze Root Cause',
        4: 'Triage Status',
        5: 'Action Taken',
        6: 'Tool Status',
        7: 'Recommendation'
    }

    timeline_data = []

    for i in range(1, case + 1):
        stage = stage_names.get(i)
        if not stage:
            continue

        if i == case and error:
            timeline_data.append({
                "stage": stage,
                "status": "error",
                "errorMessage": error
            })
        else:
            timeline_data.append({
                "stage": stage,
                "status": "success",
                "errorMessage": ""
            })

    return {
        "agent.timeline.updated": {
            "alert_id":alertid,
            "data": timeline_data
        }
    }


"""
timelineStages
  'Received Alert' case 1
  'Type Agent' case 2
  'Analyze Root Cause' case 3
  'Triage Status' case 4
  'Action Taken' case 5
  'Tool Status' case 6
  'Recommendation' case 7
"""

"""
    'agent.timeline.updated': {
        alert_id : "str"
        data: [
            {
            stage: 'Received Alert',
            status: 'success',
            errorMessage: '',
            },
            {
            stage: 'Type Agent',
            status: 'success',
            errorMessage: '',
            },
        ],
    }
"""