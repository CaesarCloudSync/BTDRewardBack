# TODO BTDGCMeet

1. Use API request to create Google Meeting
2. When created store in redis spaces:*id : meeting_uri | duration | recurring | timeshosted = 0
2. Schedule BTDGCMeetSub to run 24 times a day for max 5 minutes each time.
3. * When conference is created creates conference redis conferences:*id : time started
4. * When user joins store in redis attendee-sessions:*userid : conferenceid|timestamp
5. * When user leaves find difference between redis time started and time.now(), then find the amount percentage against the spaces duration
6. * When conference ends remove attendee-sessions,conferences. Check if spaces:*d timeshosted is equal: yes then remove space else: increment times hosted by one. else 
7. * When user leaves assign tokens if time spent in session is more than 80%.