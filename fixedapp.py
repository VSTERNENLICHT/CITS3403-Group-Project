@app.route('/api/results')
@login_required
def get_results_data():
    gpa = GPA.query.filter_by(user_id=current_user.id).first()
    wam = WAM.query.filter_by(user_id=current_user.id).first()
    goal = Goal.query.filter_by(user_id=current_user.id).first()

    if not gpa or not wam:
        return jsonify({"error": "GPA or WAM data missing"}), 404

    # Dynamically extract semester GPA/WAM fields
    def extract_semesters(obj):
        semesters = {}
        for field in obj.__table__.columns.keys():
            if field.startswith("year_") and field != "user_id":
                # Format label like "1 Sem 1"
                year_sem = field.replace("year_", "").replace("_semester_", " Sem ")
                value = getattr(obj, field)
                if value != -1:  # Skip no-data marker
                    semesters[year_sem] = value
        return semesters

    response = {
        "gpa": round(gpa.final_gpa, 2),
        "wam": round(wam.final_wam, 2),
        "desired_gpa": round(goal.gpa, 2) if goal else None,
        "desired_wam": round(goal.wam, 2) if goal else None,
        "gpa_semesters": extract_semesters(gpa),
        "wam_semesters": extract_semesters(wam)
    }

    return jsonify(response)
