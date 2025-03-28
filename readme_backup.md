In this project, we will use Python to call Canvas API to get the student's academic performance data.

We will mainly focus on 2 datasets:
1. ALL student's currently enrolled courses' scores.
2. ALL student's currently enrolled courses' assignment status (submitted, graded, late, etc.).

Then we will use these data to update the databased in Lark and Notion for later use and visualization.

More detailed explaination:

Dataset 1 Scores:
The dataset should include the following information:
- Student Name: Directly from Canvas API
- Student Chinese Name: Mapping from Student Name
- Student Prefered English Name: Mapping from Student Name
- Course Name: Directly from Canvas API
- Course Name in Chinese: Mapping from Course Name
- Score: Directly from Canvas API
- Grade: Simple mapping: 90-100 A, 80-89 B, 70-79 C, 60-69 D, 0-59 F
- Fetch Time: When the data is fetched. YYYY-MM-DD HH:MM:SS

We ALWAYS append the new data to the existing dataset. 

Dataset 2 Assignment Status:
The dataset should include the following information:
- Student Name: Directly from Canvas API
- Student Chinese Name: Mapping from Student Name
- Student Prefered English Name: Mapping from Student Name
- Course Name: Directly from Canvas API
- Course Name in Chinese: Mapping from Course Name
- Course Academic Support: Mapping from Academic Support Mapping
- Assignment Name: Directly from Canvas API
- Assignment ID: Directly from Canvas API
- Assignment Due Date: Directly from Canvas API
- Assignment Submission Time: Directly from Canvas API, May be date data or Not submitted
- Assignment Full Mark: Directly from Canvas API
- Assignment Student Score: Directly from Canvas API
- Assignment Status: Directly from Canvas API
- Fetch Time: When the data is fetched. YYYY-MM-DD HH:MM:SS

We DO NOT ALWAYS append the new data to the existing dataset. 
We apply a speicifc rule for data update:
1. If the assignment is new, we append the data to the existing dataset.
2. If the assignment is not new, we only update the assignment data as in: fetch time, assignment status, assignment student score.
This make sure there is only one record for each assignment and avoid duplicate data.


The data later will be used in Lark and Notion via their API. We hold this part at the moment.

