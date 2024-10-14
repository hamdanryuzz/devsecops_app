import streamlit as st
from db_utils import get_database_connection
import uuid
import random
import string
import pandas as pd

def generate_random_id():
    return str(uuid.uuid4())[:8]
    
def get_users_by_role(role):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, username FROM user WHERE role = %s"
    cursor.execute(query, (role,))
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def user_dropdown(role, label):
    users = get_users_by_role(role)
    user_options = [user['username'] for user in users]
    pic_username = st.selectbox(label, user_options)
    pic_id = next((user['id'] for user in users if user['username'] == pic_username), None)
    return pic_id

def get_jenis_by_stage(stage):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT jenis_id, deskripsi_jenis FROM jenis WHERE stage = %s"
    cursor.execute(query, (stage,))
    jenis = cursor.fetchall()
    cursor.close()
    conn.close()
    return jenis

def get_status_step():
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id_status_detail, deskripsi FROM status_step"
    cursor.execute(query)
    steps = cursor.fetchall()
    cursor.close()
    conn.close()
    return steps

def get_status_step_detail():
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id_status_detail, deskripsi FROM status_step_detail"
    cursor.execute(query)
    steps = cursor.fetchall()
    cursor.close()
    conn.close()
    return steps


def main_page():
    if st.button('Back'):
        st.session_state['page'] = 'main_page'
    st.subheader('Project Page')
    if st.button("Create New Project"):
        st.session_state['page'] = 'create_project_page'

    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            p.project_id,
            p.nama_project,
            ud.username as design_pic,
            udv.username as develop_pic,
            ub.username as build_pic,
            ut.username as test_pic,
            udp.username as deploy_pic,
            um.username as monitor_pic,
            u.username as pm
        FROM 
            project p
        LEFT JOIN 
            design d ON p.design_id = d.design_id
        LEFT JOIN 
            user ud ON d.pic = ud.id
        LEFT JOIN 
            develop dv ON p.develop_id = dv.develop_id
        LEFT JOIN 
            user udv ON dv.pic = udv.id
        LEFT JOIN 
            build b ON p.build_id = b.build_id
        LEFT JOIN 
            user ub ON b.pic = ub.id
        LEFT JOIN 
            test t ON p.test_id = t.test_id
        LEFT JOIN 
            user ut ON t.pic = ut.id
        LEFT JOIN 
            deploy dp ON p.deploy_id = dp.deploy_id
        LEFT JOIN 
            user udp ON dp.pic = udp.id
        LEFT JOIN 
            monitor m ON p.monitor_id = m.monitor_id
        LEFT JOIN 
            user um ON m.pic = um.id
        LEFT JOIN 
            user u ON p.pic = u.id
    """
    cursor.execute(query)
    projects = cursor.fetchall()
    cursor.close()
    conn.close()

    if projects:
        df = pd.DataFrame(projects)
        columns_order = ['Project ID', 'Nama Project', 'PIC Design', 'PIC Develop', 'PIC Build', 'PIC Test', 'PIC Deploy', 'PIC Monitor', 'PM']
        df.columns = columns_order
        st.write("Projects:")
        st.dataframe(df, hide_index=True)
    else:
        st.write("No projects found.")

def create_project_page():
    if st.button('Back'):
        st.session_state['page'] = 'project'
        st.rerun()

    st.subheader("Create New Project")
    with st.form("create_project"):
        nama_project = st.text_input("Nama Project")
        project_id = generate_random_id()
        design_id = generate_random_id()
        develop_id = generate_random_id()
        build_id = generate_random_id()
        test_id = generate_random_id()
        deploy_id = generate_random_id()
        monitor_id = generate_random_id()
        pic_id = user_dropdown('pm', "PIC PM")
        pic_design = user_dropdown('design', "PIC Design")
        pic_develop = user_dropdown('develop', "PIC Develop")
        pic_build = user_dropdown('build', "PIC Build")
        pic_test = user_dropdown('test', "PIC Test")
        pic_deploy = user_dropdown('deploy', "PIC Deploy")
        pic_monitor = user_dropdown('monitor', "PIC Monitor")
        status_steps = get_status_step()
        status_options = {'-': '-', **{step['deskripsi']: step['id_status_detail'] for step in status_steps}}

        status_steps2 = get_status_step_detail()
        status_options2 = {'-': '-', **{step['deskripsi']: step['id_status_detail'] for step in status_steps2}}

        previous = st.selectbox("Previous", options=list(status_options.keys()), format_func=lambda x: x)
        current = st.selectbox("Current", options=list(status_options2.keys()), format_func=lambda x: x)
        next = st.selectbox("Next", options=list(status_options.keys()), format_func=lambda x: x)

        if st.form_submit_button("Create Project"):
            conn = get_database_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM design WHERE design_id = %s"
            cursor.execute(query, (design_id,))
            if not cursor.fetchone():
                query = "INSERT INTO design (design_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (design_id,pic_design))
                conn.commit()

                design_jenis = get_jenis_by_stage('design')
                for jenis in design_jenis:
                    
                    query = "INSERT INTO detail_design (id_detail_design, id_design, jenis_id, information) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (generate_random_id(), design_id, jenis['jenis_id'], ''))
                    conn.commit()
            

            query = "SELECT * FROM develop WHERE develop_id = %s"
            cursor.execute(query, (develop_id,))
            if not cursor.fetchone():
                query = "INSERT INTO develop (develop_id,pic) VALUES (%s,%s)"
                cursor.execute(query, (develop_id,pic_develop))
                conn.commit()

            query = "SELECT * FROM build WHERE build_id = %s"
            cursor.execute(query, (build_id,))
            if not cursor.fetchone():
                query = "INSERT INTO build (build_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (build_id,pic_build))
                conn.commit()

            query = "SELECT * FROM test WHERE test_id = %s"
            cursor.execute(query, (test_id,))
            if not cursor.fetchone():
                query = "INSERT INTO test (test_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (test_id, pic_test))
                conn.commit()

            query = "SELECT * FROM deploy WHERE deploy_id = %s"
            cursor.execute(query, (deploy_id,))
            if not cursor.fetchone():
                query = "INSERT INTO deploy (deploy_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (deploy_id, pic_deploy))
                conn.commit()

            query = "SELECT * FROM monitor WHERE monitor_id = %s"
            cursor.execute(query, (monitor_id,))
            if not cursor.fetchone():
                query = "INSERT INTO monitor (monitor_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (monitor_id, pic_monitor))
                conn.commit()

            previous_id = status_options[previous]
            current_id = status_options2[current]
            next_id = status_options[next]

            query = "INSERT INTO project (project_id, design_id, develop_id, build_id, test_id, deploy_id, monitor_id, pic, nama_project, previous, current, next) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (project_id, design_id, develop_id, build_id, test_id, deploy_id, monitor_id, pic_id, nama_project, previous_id, current_id, next_id))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Project created successfully!")