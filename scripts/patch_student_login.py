import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix student login to also store student_id
old_login = (
    '                    if row:\n'
    '                        st.session_state.role = "student"\n'
    '                        st.session_state.student_name = row[0]\n'
    '                        st.session_state.student_no = row[1]\n'
    '                        st.rerun()'
)

new_login = (
    '                    if row:\n'
    '                        st.session_state.role = "student"\n'
    '                        st.session_state.student_name = row[0]\n'
    '                        st.session_state.student_no = row[1]\n'
    '                        # student_id\'yi de kaydet (risk haritasi icin)\n'
    '                        conn2 = sqlite3.connect(DATABASE_PATH)\n'
    '                        row2 = conn2.execute("SELECT id FROM students WHERE UPPER(pin) = UPPER(?)", (pin_input.strip(),)).fetchone()\n'
    '                        conn2.close()\n'
    '                        if row2:\n'
    '                            st.session_state.student_id = row2[0]\n'
    '                        st.rerun()'
)

if old_login in content:
    content2 = content.replace(old_login, new_login, 1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content2)
    print("SUCCESS: student_id saved to session_state")
else:
    print("NOT FOUND - manual check needed")
    # show context
    idx = content.find('session_state.role = "student"')
    print(repr(content[idx-100:idx+200]))
