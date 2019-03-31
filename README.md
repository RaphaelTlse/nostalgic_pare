# nostalgic_pare
Project made during the 2019 School of AI Health Hackathon

### setup instructions
data should be put in a data folder at the root of the project
python version Python 3.5.1, and other dependancies are listed in the ```requirements.txt``` file

### achievements
#### improved user interface
We have proposed a new enhanced user interface, leveraging the user's goals in data collection for a personnalized experience, and have hints to offer personnalized advanced insights, like early pregnancy detection, symptoms anomaly, and endometriosis suspecions

![alt text](image/mockup_iphone.png){:height="300px" width="200px"}

#### results on pregnancy detection
We have clustered cycles based on their lengths, and anomalies of length compared to the users' other cycles. A cluster (blue in the plot below) represents cycles that are significantly longer than the user's usual and may be pregnant and should monitor their period closely.

![alt text](image/cycle_clustering.png)

#### results on symptoms to cycle matching
The objective of this analysis is to correlate the variations of symptoms with the day of the cycle. For all users, cycle length was normalized to a "standard" 28-day cycle, and the mean intensity of symptoms was computed when enough different users (more than 25) logged their symptoms into the app for that day of their cycle.

We observe known patterns of pain and disorders between J1 and J5, and symptoms of pre-menstrual syndroms at the end of the cycle.

![alt text](image/symptom_cycle_match.png) 

To obtain the matching of one user's symptoms with respect to "normal" symptoms, one needs to compute the cosine similarity between user's symptoms vector and the average vector for that day of the cycle. A similarity close to 1 indicates that the symptoms matched what is expected at that time of the cycle, otherwise, it means that symptoms may have other causes, and indicate another disorder if symptoms persist.

#### results on endometriosis suspiscion
the objective of this analysis is to detect if some users have symptoms of endometriosis, that is accute pain during period ("cramp" in the data). We isolate the users with most accurate pain at J1 of the cycle, and observe their other symptoms. Although the sample is small we see that this "severe pain" population (16 patients) exhibits high intensity of other endometriosis symptoms: backpain, bloating, sore, but not for other symptoms, like diarrhea or dizziness. A larger sample is needed to have deeper statistical analyses.

![alt text](image/endometriosis.png) 

The ideal would be to have the endometriosis diagnosis in the data themselves (i.e. the app asks users), so that the diagnosis could maybe be predicted for other similar patients, to improve suspiscion of endometriosis detection
