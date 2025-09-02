#importing flask#
from flask import Flask, render_template, request

app = Flask(__name__, template_folder="template")

#main functions#
def compute_term(term_name, absences, exam, quizzes, requirements, recitation):
    #Check if failed because of the number of absences#
    if absences >= 4:
        return None, f"{term_name} FAILED due to excessive absences."
    
    #main computation formulas#
    attendance = 100 - (absences * 10)
    classtop = (0.4 * quizzes) + (0.3 * requirements) + (0.3 * recitation)
    term_grade = (0.6 * exam) + (0.1 * attendance) + (0.3 * classtop)
    return term_grade, f"{term_name} Grade: {term_grade:.2f}"

#function to compute required final exam score#
def required_for_finals(prelim, midterm, target):
    return (target - (0.2 * prelim) - (0.3 * midterm)) / 0.5

#notifies flask when someone enteres the route#
@app.route("/", methods=["GET", "POST"])
def index():
    #getting all the required info from throughout the other files#
    fields = [
        "prelim_absences", "prelim_exam", "prelim_quizzes", "prelim_requirements", "prelim_recitation",
        "mid_absences", "mid_exam", "mid_quizzes", "mid_requirements", "mid_recitation",
        "final_absences", "final_exam", "final_quizzes", "final_requirements", "final_recitation"
    ]

    #Initialize empty values for form fields#
    values = {f: "" for f in fields}

    if request.method == "POST":
        #preserve whatever the user submitted#
        values = {f: request.form.get(f, "") for f in fields}
        try:
            #helper validators using preserved values#
            def get_int_nonneg(field, label):
                s = values.get(field, "")
                try:
                    v = int(s)
                except Exception:
                    raise ValueError(f"{label}: please enter a valid integer.")
                if v < 0:
                    raise ValueError(f"{label}: absences cannot be negative.")
                return v

            def get_grade(field, label):
                s = values.get(field, "")
                try:
                    v = float(s)
                except Exception:
                    raise ValueError(f"{label}: please enter a valid number.")
                if not (0 <= v <= 100):
                    raise ValueError(f"{label}: must be between 0 and 100.")
                return v

            #Prelim inputs#
            prelim_absences = get_int_nonneg("prelim_absences", "Prelim absences")
            prelim_exam = get_grade("prelim_exam", "Prelim exam")
            prelim_quizzes = get_grade("prelim_quizzes", "Prelim quizzes")
            prelim_requirements = get_grade("prelim_requirements", "Prelim requirements")
            prelim_recitation = get_grade("prelim_recitation", "Prelim recitation")

            #Midterm inputs#
            mid_absences = get_int_nonneg("mid_absences", "Midterm absences")
            mid_exam = get_grade("mid_exam", "Midterm exam")
            mid_quizzes = get_grade("mid_quizzes", "Midterm quizzes")
            mid_requirements = get_grade("mid_requirements", "Midterm requirements")
            mid_recitation = get_grade("mid_recitation", "Midterm recitation")

            #Final inputs#
            final_absences = get_int_nonneg("final_absences", "Final absences")
            final_exam = get_grade("final_exam", "Final exam")
            final_quizzes = get_grade("final_quizzes", "Final quizzes")
            final_requirements = get_grade("final_requirements", "Final requirements")
            final_recitation = get_grade("final_recitation", "Final recitation")

        except ValueError as e:
            #re-render form with error and previously entered values#
            return render_template("main.html", error=str(e), values=values)

        #Compute each term#
        prelim, prelim_msg = compute_term("Prelim", prelim_absences, prelim_exam, prelim_quizzes, prelim_requirements, prelim_recitation)
        midterm, midterm_msg = compute_term("Midterm", mid_absences, mid_exam, mid_quizzes, mid_requirements, mid_recitation)
        finals, final_msg = compute_term("Final", final_absences, final_exam, final_quizzes, final_requirements, final_recitation)

        overall = None
        req75 = None
        req90 = None
        if prelim is not None and midterm is not None and finals is not None:
            overall = (0.2 * prelim) + (0.3 * midterm) + (0.5 * finals)
            req75 = required_for_finals(prelim, midterm, 75)
            req90 = required_for_finals(prelim, midterm, 90)
         
        #using the htmls to display the code#
        return render_template(
            "front.html",
            prelim_msg=prelim_msg,
            midterm_msg=midterm_msg,
            final_msg=final_msg,
            prelim=prelim,
            midterm=midterm,
            finals=finals,
            overall=overall,
            req75=req75,
            req90=req90
        )

    return render_template("main.html", values=values)

if __name__ == "__main__":
    app.run(debug=True)
