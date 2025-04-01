import requests
import csv
import json
from datetime import datetime
# API
ACCESS_TOKEN = "5495~HeUC3AawWTLy3Gf3Lf92xW9ew9tAJYGXwzVXGGT8u9fyELhuWBM3LcVPu3JYaHLe"
CANVAS_DOMAIN = "shastacollege.instructure.com"
USER_ID = 77632
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
CSV_FILENAME = "canvas_grades.csv"
# 课程中文名
COURSE_NAME_MAP = {
    "Calculus 3A - S9723 (2025S-MATH-3A)": "微积分 3A",
    "General Biology - S9768 (2025S-BIOL-10)": "生物学",
    "General Psychology - S9987 (2025S-PSYC-1A)": "心理学",
    "Music Appreciation - S8262 (2025S-MUS-10)": "音乐鉴赏",
    "Precalculus - F9621 (2024F-MATH-2)": "预微积分",
    # New course mappings
    "Introduction to Art - S8279 (2025S-ART-1)": "艺术学导论",
    "Introduction to Ethnic Studies - S9906 (2025S-ETHS-1)": "族裔研究导论",
    "Introduction to Sociology - S9999 (2025S-SOC-1)": "社会学导论",
    "Calculus 4A - S0516 (2025S-MATH-4A)": "微积分 4A",
    "Critical Reasoning/Read/Write - S9853 (2025S-ENGL-1C)": "批判性推理/阅读/写作",
    "Precalculus - S9722 (2025S-MATH-2)": "预微积分"
}
def get_student_name():
    """获取当前学生名字"""
    url = f"https://{CANVAS_DOMAIN}/api/v1/users/self/profile"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("name", "未知学生")
    return "未知学生"
def get_courses():
    """获取所有课程"""
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else None
def get_course_grades(course_id):
    """获取课程成绩"""
    url = f"https://{CANVAS_DOMAIN}/api/v1/courses/{course_id}/enrollments"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        for enrollment in data:
            if enrollment["user_id"] == USER_ID and "grades" in enrollment:
                return enrollment["grades"].get("current_score", "N/A")
    return "N/A"  # 没找到成绩
def save_to_csv(data):
    """保存数据到 CSV"""
    with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["学生名字", "学科名字（中文）", "学科名字（英文）", "当前分数", "抓取时间"])
        writer.writerows(data)
    print(f"✅ 成绩已保存到 {CSV_FILENAME}")
if __name__ == "__main__":
    student_name = get_student_name()
    print(f"📢 当前学生: {student_name}")
    courses = get_courses()
    if courses:
        grades_data = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 记录抓取时间
        for course in courses:
            course_name_en = course["name"]
            course_name_cn = COURSE_NAME_MAP.get(course_name_en, "未知课程")
            course_id = course["id"]
            print(f"\n获取 {course_name_cn} ({course_name_en}) 的成绩...")
            score = get_course_grades(course_id)
            grades_data.append([student_name, course_name_cn, course_name_en, score, timestamp])
            print(f"✅ 课程: {course_name_cn} ({course_name_en}) | 分数: {score}%")
        save_to_csv(grades_data)

