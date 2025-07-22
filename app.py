
# from datetime import date
# from flask import Flask, request, render_template, redirect, flash
# import pandas as pd

# app = Flask(__name__)
# app.secret_key = 'project-validator-2024'

# def validate_project_data(df):
#     today = date.today()
#     stats = {
#         'missing_dates': 0,
#         'invalid_range': 0,
#         'future_start': 0,
#         'too_long': 0
#     }
#     issues = []

#     # Normalize date columns
#     df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
#     df['End Date']   = pd.to_datetime(df['End Date'],   errors='coerce')

#     for idx, row in df.iterrows():
#         msgs = []
#         pn = row.get('Project Name', f'Row {idx+2}')
#         sd, ed = row['Start Date'], row['End Date']

#         # Rule 1
#         if pd.isna(sd) or pd.isna(ed):
#             msgs.append("Missing start date or end date")
#             stats['missing_dates'] += 1
#         else:
#             sd_d = sd.date()
#             ed_d = ed.date()
#             # Rule 2
#             if sd_d > ed_d:
#                 msgs.append("Start date is after end date")
#                 stats['invalid_range'] += 1
#             # Rule 3
#             if sd_d > today:
#                 msgs.append("Start date is in the future")
#                 stats['future_start'] += 1
#             # Rule 4
#             if (ed_d - sd_d).days > 730:
#                 msgs.append("Project duration exceeds 2 years")
#                 stats['too_long'] += 1

#         if msgs:
#             issues.append({
#                 'row_number': idx + 2,
#                 'project_name': pn,
#                 'start_date': sd.strftime('%Y-%m-%d') if not pd.isna(sd) else 'Missing',
#                 'end_date':   ed.strftime('%Y-%m-%d') if not pd.isna(ed) else 'Missing',
#                 'messages':   msgs
#             })

#     return issues, stats

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         f = request.files.get('file')
#         if not f or not f.filename.endswith('.xlsx'):
#             flash('Please upload a valid .xlsx file')
#             return redirect(request.url)

#         df = pd.read_excel(f)
#         for col in ['Project Name', 'Start Date', 'End Date']:
#             if col not in df.columns:
#                 flash(f'Missing column: {col}')
#                 return redirect(request.url)

#         issues, stats = validate_project_data(df)
#         total_rows   = len(df)
#         total_issues = sum(stats.values())

#         return render_template(
#             'report.html',
#             issues=issues,
#             stats=stats,
#             total_rows=total_rows,
#             total_issues=total_issues
#         )

#     return render_template('upload.html')

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)




from datetime import date
from flask import Flask, request, render_template, redirect, flash
import pandas as pd

app = Flask(__name__)
app.secret_key = 'project-validator-2024'

def validate_project_data(df):
    today = date.today()
    stats = {
        'missing_dates': 0,
        'invalid_range': 0,
        'future_start': 0,
        'too_long': 0
    }
    issues = []

    # Normalize date columns
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    df['End Date']   = pd.to_datetime(df['End Date'],   errors='coerce')

    for idx, row in df.iterrows():
        issue_types = []  # Track individual issue types for this row
        pn = row.get('Project Name', f'Row {idx+2}')
        sd, ed = row['Start Date'], row['End Date']

        # Rule 1 - Missing Dates
        if pd.isna(sd) or pd.isna(ed):
            issue_types.append({
                'type': 'missing_dates',
                'message': 'Missing start date or end date'
            })
            stats['missing_dates'] += 1

        if not pd.isna(sd) and not pd.isna(ed):
            sd_d = sd.date()
            ed_d = ed.date()
            
            # Rule 2 - Invalid Range
            if sd_d > ed_d:
                issue_types.append({
                    'type': 'invalid_range',
                    'message': 'Start date is after end date'
                })
                stats['invalid_range'] += 1
            
            # Rule 3 - Future Start
            if sd_d > today:
                issue_types.append({
                    'type': 'future_start',
                    'message': 'Start date is in the future'
                })
                stats['future_start'] += 1
            
            # Rule 4 - Too Long
            if (ed_d - sd_d).days > 730:
                issue_types.append({
                    'type': 'too_long',
                    'message': 'Project duration exceeds 2 years'
                })
                stats['too_long'] += 1

        if issue_types:
            issues.append({
                'id': f"issue_{idx + 2}",  # Unique identifier
                'row_number': idx + 2,
                'project_name': pn,
                'start_date': sd.strftime('%Y-%m-%d') if not pd.isna(sd) else 'Missing',
                'end_date':   ed.strftime('%Y-%m-%d') if not pd.isna(ed) else 'Missing',
                'issue_types': issue_types,
                'resolved': False
            })

    return issues, stats

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files.get('file')
        if not f or not f.filename.endswith('.xlsx'):
            flash('Please upload a valid .xlsx file')
            return redirect(request.url)

        df = pd.read_excel(f)
        for col in ['Project Name', 'Start Date', 'End Date']:
            if col not in df.columns:
                flash(f'Missing column: {col}')
                return redirect(request.url)

        issues, stats = validate_project_data(df)
        total_rows   = len(df)
        total_issues = len(issues)

        return render_template(
            'report.html',
            issues=issues,
            stats=stats,
            total_rows=total_rows,
            total_issues=total_issues
        )

    return render_template('upload.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

