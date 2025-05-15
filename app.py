@app.route('/api/results')
@login_required
def get_results_data():
    gpa = GPA.query.filter_by(user_id=current_user.id).first()
    wam = WAM.query.filter_by(user_id=current_user.id).first()
    goal = Goal.query.filter_by(user_id=current_user.id).first()

    if not gpa or not wam:
        return jsonify({"error": "GPA or WAM data missing"}), 404

    response = {
        "gpa": round(gpa.final_gpa, 2),
        "wam": round(wam.final_wam, 2),
        "desired_gpa": round(goal.gpa, 2) if goal else None,
        "desired_wam": round(goal.wam, 2) if goal else None,
        "gpa_semesters": {
            "sem1_yr1": gpa.year_1_semester_1,
            "sem2_yr1": gpa.year_1_semester_2,
            "sem1_yr2": gpa.year_2_semester_1,
            "sem2_yr2": gpa.year_2_semester_2
        },
        "wam_semesters": {
            "sem1_yr1": wam.year_1_semester_1,
            "sem2_yr1": wam.year_1_semester_2,
            "sem1_yr2": wam.year_2_semester_1,
            "sem2_yr2": wam.year_2_semester_2
        }
    }

    return jsonify(response)
