# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 14:34:13 2022

@author: hannah.carroll
"""

import simpy
import random
import pandas as pd
import numpy as np
import streamlit as st

class g:
    with st.sidebar:
        mean_new = st.number_input("Mean number of new patients per week", 
                                   min_value=0.0, max_value=200.0, value=65.0)
        percent_prefer_eve = st.number_input("Percentage of patients who "
                                             "prefer evening appointments", 
                                          min_value = 0.0, max_value=100.0, 
                                          value=13.3)
        prob_prefer_eve = percent_prefer_eve/100
        percent_prefer_f2f = st.number_input("Percentage of patients who "
                                            "prefer face to face appointments", 
                                          min_value = 0.0, max_value=100.0, 
                                          value=20.8)
        prob_prefer_f2f = percent_prefer_f2f/100
        percent_priority = st.number_input("Percentage patients who are "
                                        "priority patients", min_value = 0.0, 
                                        max_value=100.0, value=14.0)
        prob_priority = percent_priority/100
        percent_ieso = st.number_input("Percentage of patients who are "
                                       "referred to IESO", min_value = 0.0, 
                                       max_value=100.0, value=10.0)
        prob_refer_ieso = percent_ieso/100
        percent_121 = st.number_input("Percentage of patients who are "
                                      "referred to 121 therapy", 
                                      min_value = 0.0, max_value=100.0, 
                                      value=72.0)
        prob_refer_121 = percent_121/100
        percent_group = st.number_input("Percentage of patients who are "
                                        "referred to group therapy", 
                                        min_value = 0.0, max_value=100.0, 
                                        value=18.0)
        prob_refer_group = percent_group/100
        mean_wait_ieso = st.number_input("Mean number of weeks patients wait "
                                         "for IESO", min_value = 0.0, 
                                         max_value = 52.0,value = 5.93)
        sess_no_group = st.number_input("(Mean) number of sessions for a full "
                                        "course of group therapy", 
                                        min_value = 1, max_value = 25, 
                                        value = 12)
        mean_sess_no_121 = st.number_input("Mean number of sessions patients "
                                           "undertake for 121 therapy", 
                                           min_value = 1, max_value = 30, 
                                           value = 13)
        mean_sess_no_ieso = st.number_input("Mean number of sessions patients "
                                            "undertake for IESO", 
                                            min_value = 1.0, max_value = 30.0, 
                                            value = 9.41)
        num_group_spaces_v = st.number_input("Number of spaces available on "
                                             "each virtual group", 
                                             min_value = 2, max_value = 20, 
                                             value = 14)
        num_group_spaces_f2f = st.number_input("Number of spaces available on "
                                               "each F2F group", min_value = 2, 
                                               max_value = 20, value = 14)
        num_v_eve_groups = st.number_input("Number of virtual evening groups "
                                           "running per week", min_value = 1, 
                                           max_value = 30, value = 4)
        num_v_day_groups = st.number_input("Number of virtual daytime groups "
                                           "running per week", min_value = 1, 
                                           max_value = 30, value = 15)  
        num_F2F_eve_groups = st.number_input("Number of face to face evening "
                                             "groups running per week", 
                                             min_value = 0, max_value = 30, 
                                             value = 0)
        num_F2F_day_groups = st.number_input("Number of face to face daytime "
                                             "groups running per week", 
                                             min_value = 0, max_value = 30, 
                                             value = 0)  
        num_app_121_f2f_eve = st.number_input("Number of evening face to face "
                                              "121 appointments available per "
                                              "week", min_value = 1, 
                                              max_value = 30, value = 12)
        num_app_121_v_eve = st.number_input("Number of evening virtual 121 "
                                            "appointments available per week", 
                                            min_value = 1, max_value = 100, 
                                            value = 44)
        num_app_121_f2f_day = st.number_input("Number of daytime face to face "
                                              "121 appointments available per "
                                              "week", min_value = 1, 
                                              max_value = 400, value = 77)
        num_app_121_v_day = st.number_input("Number of daytime virtual 121"
                                            " appointments available per week", 
                                            min_value = 1, max_value = 400, 
                                            value = 293)
        
    inter_arrival = 1/mean_new
    num_app_ieso = 9999999 #unlimited number of ieso appointments
    num_app_group_v_eve = num_group_spaces_v*num_v_eve_groups 
    #num virtual evening group appointments available per week
    num_app_group_v_day = num_group_spaces_v*num_v_day_groups
    #num virtual daytime group appointments available per week
    num_app_group_f2f_eve = num_group_spaces_f2f*num_F2F_eve_groups 
    #num F2F evening group appointments available per week
    num_app_group_f2f_day = num_group_spaces_f2f*num_F2F_day_groups
    #num F2F daytime group appointments available per week
    
    current_q_df = pd.DataFrame()
    current_q_df["P_ID"] = []
    current_q_df["Evening Appt?"] = []
    current_q_df["Priority Patient?"] = []
    current_q_df["Need F2F?"] = []
    current_q_df["Started Queueing"] = []
    current_q_df["Stage"] = []
    current_q_df.set_index("P_ID", inplace=True)
    
    completed_df = pd.DataFrame()
    completed_df["P_ID"] = []
    completed_df["Evening Appt?"] = []
    completed_df["Priority Patient?"] = []
    completed_df["Need F2F?"] = []
    current_q_df["Started Queueing"] = []
    current_q_df["Finished Queueing"] = []
    completed_df["Wait time"] = []
    completed_df["Stage"] = []
    completed_df["No of Appts"] = []
    completed_df.set_index("P_ID", inplace=True)
    
    duration = 52
    num_runs = 1
    warm_up = 104
    sim_duration = warm_up + duration
    
class Patient:
    def __init__(self, p_id):
        self.p_id = p_id
        self.q_start = np.nan
        self.q_end = np.nan
        self.wait_time = np.nan
        self.appointments = 0
        self.eve_prefer = False
        self.f2f_prefer = False
        x = random.random()
        y = random.random()
        
        #What treatment are they referred to?
        if x < g.prob_refer_ieso:
            self.treatment = "IESO"
        if g.prob_refer_ieso <=x< (g.prob_refer_ieso + g.prob_refer_121):
            self.treatment = "121"
        if (g.prob_refer_ieso + g.prob_refer_121) <= x:
            self.treatment = "Group"
        
        #is this a priority patient?
        if y < g.prob_priority:
            self.priority = 1
        else:
            self.priority = 2
    
class Step_3_Model:
    def __init__(self):
        self.env = simpy.Environment()
        self.patient_counter = 0
        
        #Resources - capacity is the number of that appointment type available
        #per week
        self.ieso = simpy.PriorityResource(self.env, capacity=g.num_app_ieso) 
                                                                #IESO
        self.app_group_v_eve = simpy.PriorityResource(self.env, 
                                            capacity=g.num_app_group_v_eve)
                                            #group virtual evening appointments
        self.app_group_v_day = simpy.PriorityResource(self.env, 
                                            capacity=g.num_app_group_v_day) 
                                            #group virtual daytime appointments
        if g.num_app_group_f2f_day > 0:
            self.app_group_f2f_day = simpy.PriorityResource(self.env, 
                                            capacity=g.num_app_group_f2f_day) 
                                            #group F2F daytime appointments
        if g.num_app_group_f2f_eve > 0:                                    
            self.app_group_f2f_eve = simpy.PriorityResource(self.env, 
                                            capacity=g.num_app_group_f2f_eve) 
                                            #group F2F evening appointments                                   
        self.app_121_f2f_eve = simpy.PriorityResource(self.env, 
                                              capacity=g.num_app_121_f2f_eve) 
                                                #121 F2F evening appointments
        self.app_121_v_eve = simpy.PriorityResource(self.env, 
                                            capacity=g.num_app_121_v_eve) 
                                            #121 virtual evening appointments                                  
        self.app_121_f2f_day = simpy.PriorityResource(self.env, 
                                              capacity=g.num_app_121_f2f_day) 
                                                #121 F2F daytime appointments
        self.app_121_v_day = simpy.PriorityResource(self.env, 
                                            capacity=g.num_app_121_v_day) 
                                            #121 virtual daytime appointments
    
    #Function to update dataframes when patient reaches treatment stage                                        
    def data_function(self, p):
        #Remove patient from queue DF
        g.current_q_df = g.current_q_df.drop(p.p_id)
            
        #Append patient info to completed DF (post warm up only)
        if self.env.now > g.warm_up:
            df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                      "Evening Appt?":[p.eve_prefer],
                                      "Need F2F?":[p.f2f_prefer],
                                      "Priority Patient?":[p.priority],
                                      "Started Queueing":[p.q_start],
                                      "Finished Queueing":[p.q_end],
                                      "Wait time":[p.wait_time],
                                      "Stage":[p.treatment],
                                      "No of Appts":[p.appointments]})
            df_to_add.set_index("P_ID", inplace=True)
            g.completed_df = g.completed_df.append(df_to_add)
        
    #Patients join the system once they have had their assessment or review     
    def generate_patients(self):
        while True:
            self.patient_counter += 1
            p = Patient(self.patient_counter)
            p.q_start = self.env.now
            
            #does patient prefer evening appointments? 
            #(group & 121 patients only)
            if p.treatment == "121" or p.treatment == "Group":
                x=random.random()
                if x < g.prob_prefer_eve:
                    p.eve_prefer = True
                else:
                    p.eve_prefer = False
       
            #does patient prefer F2F appointments? (121 patients)
            if p.treatment=="121":
                y=random.random()
                if y < g.prob_prefer_f2f:
                    p.f2f_prefer = True
                else:
                    p.f2f_prefer = False
        
            #does patient prefer F2F appointments? (group patients)
            if p.treatment == "Group" and (g.num_app_group_f2f_eve>0 or
                                                    g.num_app_group_f2f_day>0):
                z=random.random()
                if z < g.prob_prefer_f2f:
                    p.f2f_prefer = True
                else:
                    p.f2f_prefer = False
                    
            df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                      "Evening Appt?":[p.eve_prefer],
                                      "Need F2F?":[p.f2f_prefer],
                                      "Priority Patient?":[p.priority],
                                      "Started Queueing":[p.q_start],
                                      "Stage":[p.treatment]})
            df_to_add.set_index("P_ID", inplace=True)
            g.current_q_df = g.current_q_df.append(df_to_add)
            
            if p.treatment == "IESO":
                self.env.process(self.attend_ieso(p))
            elif p.treatment == "121":
                self.env.process(self.attend_121(p))
            elif p.treatment == "Group":
                self.env.process(self.attend_group(p))
            
            sampled_interarrival = random.expovariate(1.0 / g.inter_arrival)
            yield self.env.timeout(sampled_interarrival)
            
    #after being referred, patients wait for an appointment to become available
    #then use that appointment for a certain number of weeks
    
    #May need to set a limit on how long IESO can wait?
        
    def attend_ieso(self, p):
        #As ieso is unlimited, sample wait time based on mean
        sampled_ieso_wait = random.expovariate(1.0 / g.mean_wait_ieso)
        #wait for that time
        yield self.env.timeout(sampled_ieso_wait)
            
        #grab an ieso appointment
        with self.ieso.request(priority=p.priority) as req:
            yield req
            #calculate the patient's wait time
            p.q_end = self.env.now
            p.wait_time = p.q_end - p.q_start
            
            #sample the number of appointments patient will attend
            p.appointments = 1 + int(random.expovariate(1.0 / 
                                                    (g.mean_sess_no_ieso - 1)))
            #update dataframes
            self.data_function(p)
            
            #hold the appointment for the sampled number of weeks
            yield self.env.timeout(p.appointments)
        #Exit point
        
    def attend_121(self, p):
        #Request the relevant appointment and wait until one is available
        if p.eve_prefer == True and p.f2f_prefer == True:
            with self.app_121_f2f_eve.request(priority=p.priority) as req:
                yield req
                
                #Calculate the wait time
                p.q_end = self.env.now
                p.wait_time = p.q_end - p.q_start
                
                #Sample the number of appointments patient will attend
                p.appointments = 1 + int(random.expovariate(1.0/(g.mean_sess_no_121 - 1)))
                
                #update dataframes
                self.data_function(p)
                
                #Hold for sampled number of weeks
                yield self.env.timeout(p.appointments)
                #Exit point
                
        elif p.eve_prefer == True and p.f2f_prefer == False:
            with self.app_121_v_eve.request(priority=p.priority) as req:
                yield req
                #Calculate the wait time and add to dataframe
                p.q_end = self.env.now
                p.wait_time = p.q_end - p.q_start
                
                #Sample the number of appointments patient will attend
                p.appointments = 1 + int(random.expovariate(
                    1.0/(g.mean_sess_no_121 - 1)))
                
                #update dataframes
                self.data_function(p)
                
                #Hold for sampled number of weeks
                yield self.env.timeout(p.appointments)
                #Exit point
                
        elif p.eve_prefer == False and p.f2f_prefer == True:
            with self.app_121_f2f_day.request(priority=p.priority) as req:
                yield req
                p.q_end = self.env.now
                
                #Calculate wait time
                p.wait_time = p.q_end - p.q_start
                
                #Sample the number of appointments patient will attend
                p.appointments = 1 + int(random.expovariate(1.0/
                                                    (g.mean_sess_no_121 - 1)))
                
                #update dataframes
                self.data_function(p)
                
                #Hold for sampled number of weeks
                yield self.env.timeout(p.appointments)
                #Exit point
                
        elif p.eve_prefer == False and p.f2f_prefer == False:
            with self.app_121_v_day.request(priority=p.priority) as req:
                yield req
                
                #Calculate wait time
                p.q_end = self.env.now
                p.wait_time = p.q_end - p.q_start
                
                #Sample the number of appointments patient will attend
                p.appointments = 1 + int(random.expovariate(1.0/
                                                    (g.mean_sess_no_121 - 1)))
                
                #update dataframes
                self.data_function(p)
                
                #Hold for sampled number of weeks
                yield self.env.timeout(p.appointments)
                #Exit point
                
    def attend_group(self, p):
        #Request the relevant appointment and wait until one is available
        if g.num_F2F_eve_groups > 0:
            if p.eve_prefer == True and p.f2f_prefer == True:
                with self.app_group_f2f_eve.request(priority=p.priority) as req:
                    yield req
                    
                    #Calculate wait time
                    p.q_end = self.env.now
                    p.wait_time = p.q_end - p.q_start
                    
                    #Number of appointments patient will attend
                    p.appointments = g.sess_no_group
                    
                    #update dataframes
                    self.data_function(p)
                    
                    #Hold for the specified number of weeks
                    yield self.env.timeout(g.sess_no_group)
                    #Exit point
        if g.num_F2F_day_groups > 0:
            if p.eve_prefer == False and p.f2f_prefer == True:
                with self.app_group_f2f_day.request(priority=p.priority) as req:
                    yield req
                    
                    #Calculate wait time
                    p.q_end = self.env.now
                    p.wait_time = p.q_end - p.q_start
                    
                    #Number of appointments patient will attend
                    p.appointments = g.sess_no_group
                    
                    #update dataframes
                    self.data_function(p)
                    
                    #Hold for the specified number of weeks
                    yield self.env.timeout(g.sess_no_group)
                    #Exit point
        if p.eve_prefer == True and p.f2f_prefer == False:
            with self.app_group_v_eve.request(priority=p.priority) as req:
                yield req
                    
                #Calculate wait time
                p.q_end = self.env.now
                p.wait_time = p.q_end - p.q_start
                
                #Number of appointments patient will attend
                p.appointments = g.sess_no_group
                    
                #update dataframes
                self.data_function(p)
                
                #Hold for the specified number of weeks
                yield self.env.timeout(g.sess_no_group)
                #Exit point                
        if p.eve_prefer == False and p.f2f_prefer == False:
            with self.app_group_v_day.request(priority=p.priority) as req:
                    yield req
                    
                    #Calculate wait time
                    p.q_end = self.env.now
                    p.wait_time = p.q_end - p.q_start
                    
                    #Number of appointments patient will attend
                    p.appointments = g.sess_no_group
                    
                    #update dataframes
                    self.data_function(p)
                    
                    #Hold for the specified number of weeks
                    yield self.env.timeout(g.sess_no_group)
                    #Exit point
                    
    def run(self):
        self.env.process(self.generate_patients())
        self.env.run(until=g.sim_duration)
    
st.title("Steps 2 Wellbeing Discrete Event Simulation") 
"Please set your parameters on the left hand side, then press Run"
#Expanders with further explanation of the model
f1 = open("variables_explanation_text.txt", 'r')
variables_explanation = f1.read()
f2 = open("further_explanation.txt", "r")
information = f2.read()
with st.expander("Click here for more information on this tool"):
    st.write(information)
with st.expander("Click here to see a detailed explanation of the variables" 
                 "on the left"):
    st.write(variables_explanation)
if st.button("Run"):
    model = Step_3_Model()
    model.run()
     
    # For current_q change started queueing to wait time
    #Set number of appointments to 0
    
    g.current_q_df["Wait time"] = g.sim_duration - g.current_q_df[
                                                            "Started Queueing"]
    g.current_q_df["Finished Queueing"] = np.nan
    g.current_q_df["No of Appts"] = 0
    
    #new_df contains both queueing patients and completed patients
    
    df1 = g.current_q_df.copy()
    df2 = g.completed_df.copy()
    
    new_df = df1.append(df2, ignore_index=True)
    
    #Create separate dfs for each appt type, separating completed and queueing
    
    IESO_complete= g.completed_df[(g.completed_df['Stage'].isin(['IESO']))]
    IESO_waiting = g.current_q_df[(g.current_q_df['Stage'].isin(['IESO']))]
    F2F_day_121_complete = g.completed_df[(g.completed_df['Stage'] == '121') & 
                          (g.completed_df['Evening Appt?'] ==0) & 
                          (g.completed_df['Need F2F?'] ==1)]
    F2F_day_121_waiting = g.current_q_df[(g.current_q_df['Stage'] == '121') & 
                        (g.current_q_df['Evening Appt?'] ==0) &  
                        (g.current_q_df['Need F2F?'] ==1)]
    F2F_eve_121_complete=g.completed_df[(g.completed_df['Stage']=='121')& 
                        (g.completed_df['Evening Appt?'] ==1) & 
                        (g.completed_df['Need F2F?'] ==1)]
    F2F_eve_121_waiting = g.current_q_df[(g.current_q_df['Stage'] == '121') & 
                         (g.current_q_df['Evening Appt?'] ==1) & 
                         (g.current_q_df['Need F2F?'] ==1)]
    v_day_121_complete = g.completed_df[(g.completed_df['Stage'] == '121') &
                            (g.completed_df['Evening Appt?'] ==0) & 
                            (g.completed_df['Need F2F?'] ==0)]
    v_day_121_waiting = g.current_q_df[(g.current_q_df['Stage'] == '121') & 
                           (g.current_q_df['Evening Appt?'] ==0) &
                           (g.current_q_df['Need F2F?'] ==0)]
    v_eve_121_complete = g.completed_df[(g.completed_df['Stage'] =='121') & 
                            (g.completed_df['Evening Appt?'] ==1) &
                            (g.completed_df['Need F2F?'] ==0)] 
    v_eve_121_waiting = g.current_q_df[(g.current_q_df['Stage']== '121') & 
                           (g.current_q_df['Evening Appt?'] ==1) &
                           (g.current_q_df['Need F2F?'] ==0)] 
    v_day_group_complete= g.completed_df[(g.completed_df['Stage']== 'Group') & 
                          (g.completed_df['Evening Appt?'] ==0)] 
    v_day_group_waiting= g.current_q_df[(g.current_q_df['Stage'] == 'Group') & 
                         (g.current_q_df['Evening Appt?'] ==0)]
    v_eve_group_complete=g.completed_df[(g.completed_df['Stage'] == 'Group') & 
                          (g.completed_df['Evening Appt?'] ==1)] 
    v_eve_group_waiting= g.current_q_df[(g.current_q_df['Stage'] == 'Group') & 
                         (g.current_q_df['Evening Appt?'] ==1)]
    if g.num_F2F_day_groups > 0:
        f2f_day_group_complete=g.completed_df[(g.completed_df['Stage']=='Group')
                             &(g.completed_df['Evening Appt?'] ==0)
                             &(g.completed_df['Need F2F?'] ==1)]
        f2f_day_group_waiting = g.current_q_df[(g.current_q_df['Stage']=='Group')
                              &(g.current_q_df['Evening Appt?'] ==0)
                              &(g.completed_df['Need F2F?'] ==1)]
    if g.num_F2F_eve_groups > 0:
        f2f_eve_group_complete=g.completed_df[(g.completed_df['Stage']=='Group')
                               &(g.completed_df['Evening Appt?'] ==1)
                               &(g.completed_df['Need F2F?'] ==1)]
        f2f_eve_group_waiting=g.current_q_df[(g.current_q_df['Stage']=='Group')
                            &(g.current_q_df['Evening Appt?'] ==1)
                            &(g.completed_df['Need F2F?'] ==1)]
        f2f_day_group_complete=g.completed_df[(g.completed_df['Stage']=='Group')
                               &(g.completed_df['Evening Appt?'] ==0)
                               &(g.completed_df['Need F2F?'] ==1)]
        f2f_day_group_waiting=g.current_q_df[(g.current_q_df['Stage']=='Group')
                            &(g.current_q_df['Evening Appt?'] ==0)
                            &(g.completed_df['Need F2F?'] ==1)]
    priority_complete=g.completed_df [(g.completed_df['Priority Patient?']==1)]
    non_priority_complete=g.current_q_df[(g.current_q_df['Priority Patient?']==2)]
                               
    # Function for the graphs - checks how many people are queueing at each 
    #point in time
    
    def daily_df(df,name, warm_up, sim_duration, second_filter, 
                 second_filter_value, third_filter, third_filter_value): 
        if third_filter != '':
            daily_df = df[(df['Stage'].isin([name])) & (df[second_filter] == 
                                                        second_filter_value) &
                          (df[third_filter] == third_filter_value)]
        elif second_filter != '':
            daily_df = df[(df['Stage'].isin([name])) & (df[second_filter] == 
                                                        second_filter_value)]
        else:
            daily_df = df[(df['Stage'].isin([name]))]
        daily_df.drop(columns={'Stage','Evening Appt?','Need F2F?',
                               'Priority Patient?','Wait time','No of Appts'}, 
                                inplace=True)   
        daily_df['Finished Queueing'] = daily_df[
                           'Finished Queueing'].replace(np.nan,sim_duration+1)
        for i in range(warm_up, sim_duration):
            a = daily_df[(daily_df['Started Queueing'] <= i) & (
                daily_df['Finished Queueing'] > i)].count()
            if i == warm_up:
                summary = (a[0])
            else:
                summary = np.append(summary,a[0])
        
        return summary
    
    #Calls the above function to generate the data for the graphs
    
    IESO_timeline = daily_df(new_df,'IESO',g.warm_up, g.sim_duration,'','','',
                                                                           '')
    Group_timeline_day = daily_df(new_df,'Group',g.warm_up, g.sim_duration,
                                                      'Evening Appt?',0,'','')
    Group_timeline_eve = daily_df(new_df,'Group',g.warm_up, g.sim_duration,
                                                      'Evening Appt?',1,'','')
    a121_F2F_day_timeline = daily_df(new_df,'121',g.warm_up, g.sim_duration,
                                              'Need F2F?',1,'Evening Appt?',0)
    a121_virtual_day_timeline = daily_df(new_df,'121',g.warm_up, 
                               g.sim_duration,'Need F2F?',0,'Evening Appt?',0)
    a121_F2F_eve_timeline = daily_df(new_df,'121',g.warm_up, g.sim_duration,
                                              'Need F2F?',1,'Evening Appt?',1)
    a121_virtual_eve_timeline = daily_df(new_df,'121',g.warm_up, 
                               g.sim_duration,'Need F2F?',0,'Evening Appt?',1)
    
    #Average wait times for each appointment type
    #Need to add priority

    IESO_wait = round(IESO_complete['Wait time'].sum()/
                         len(IESO_complete.index),1)
    F2F_day_121_wait = round(F2F_day_121_complete['Wait time'].sum()/
                            len(F2F_day_121_complete.index),1)
    F2F_eve_121_wait = round(F2F_eve_121_complete['Wait time'].sum()/
                             len(F2F_eve_121_complete.index),1)
    v_day_121_wait = round(v_day_121_complete['Wait time'].sum()/
                            len(v_day_121_complete.index),1)
    v_eve_121_wait = round (v_eve_121_complete['Wait time'].sum()/
                             len(v_eve_121_complete.index),1)
    v_day_group_wait = round(v_day_group_complete['Wait time'].sum()/
                              len(v_day_group_complete.index),1)
    v_eve_group_wait = round(v_eve_group_complete['Wait time'].sum()/
                              len(v_eve_group_complete.index),1)
    if g.num_F2F_day_groups > 0:
        F2F_day_group_wait= round(f2f_day_group_complete['Wait time'].sum()/
                                   len(f2f_day_group_complete.index),1)
        F2F_eve_group_wait= round(f2f_eve_group_complete['Wait time'].sum()/
                                   len(f2f_eve_group_complete.index),1)
    priority_wait = round(priority_complete['Wait time'].sum()/
                                      len(priority_complete.index),1)
    non_priority_wait = round(non_priority_complete['Wait time'].sum()/
                                      len(non_priority_complete.index),1)
    
    #Turns off the arrows on the metrics
    st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    
    st.markdown('##')
    st.subheader('Summary Metrics')
    st.markdown('##')
    #Two separate tabs for patients seen and patients waiting
    tab31, tab32 = st.tabs(["Total Clients Seen", "Total Clients Waiting"])
    with tab31:
        #Metrics for patients seen separated by appointment type
        st.subheader('''Total Clients Seen''')
        col16,col17,col18,col19 = st.columns (4)
        F2F_Day_121_metric = col16.metric(label = '121 F2F day patients seen', 
                            value = f"Average wait {F2F_day_121_wait} weeks")
        F2F_Eve_121_metric = col17.metric(label = '121 F2F evening patients seen', 
                            value = f"average wait {F2F_eve_121_wait} weeks")
        v_Day_121_metric = col18.metric(label = '121 virtual day patients seen', 
                            value = f"average wait {v_day_121_wait} weeks")
        v_Eve_121_metric = col19.metric(label='121 virtual evening patients seen', 
                            value = f"average wait {v_eve_121_wait} weeks")
        IESO_metric = col16.metric(label = 'IESO patients seen', 
                            value = f"average wait {IESO_wait} weeks")
        v_Day_group_metric = col17.metric(label = 'Group virtual day patients seen', 
                            value = f"average wait {v_day_group_wait} weeks")
        v_Eve_group_metric =col18.metric(label ='Group virtual evening patients seen', 
                            value = f"average wait {v_eve_group_wait} weeks")
        if g.num_F2F_day_groups > 0:
            f2f_day_group_metric = col16.metric(label = 'Group F2F day patients seen',
                            value = f"average wait {F2F_day_group_wait} weeks")
        if g.num_F2F_eve_groups > 0:
            f2f_eve_group_metric = col17.metric(label = 'Group F2F evening patients seen',
                            value = f"average wait {F2F_eve_group_wait} weeks")
        priority_metric = col16.metric(label ='Priority patients seen',
                                value = f"average wait {priority_wait}")
        non_priority_metric = col16.metric(label ='Non-priority patients seen',
                                value = f"average wait {non_priority_wait}")

    #Metrics for patients waiting separated by appointment type
    with tab32: 
        st.subheader('''Number of waiting Clients''')
        col1,col2,col3,col4 = st.columns (4)
        if len(F2F_day_121_waiting) > 0:
            F2F_day_121_wait_q = round(F2F_day_121_waiting['Wait time'].sum()/
                                       len(F2F_day_121_waiting.index),1)
            F2F_day_121_text = f"average wait {F2F_day_121_wait_q} weeks"
        else:
            F2F_day_121_wait_q = 'WL Cleared'
            F2F_day_121_text = 'WL Cleared'
        if len(F2F_eve_121_waiting) > 0:
            F2F_eve_121_wait_q =round(F2F_eve_121_waiting['Wait time'].sum()/
                                      len(F2F_eve_121_waiting.index),1)
            F2F_eve_121_text = f"average wait {F2F_eve_121_wait_q} weeks"
        else:
            F2F_eve_121_wait_q = 'WL Cleared'
            F2F_eve_121_text = 'WL Cleared'

        if len(v_day_121_waiting) > 0:
            v_day_121_wait_q = round(v_day_121_waiting['Wait time'].sum()/
                                     len(v_day_121_waiting.index),1)
            v_day_121_text = f"average wait {v_day_121_wait_q} weeks"
        else:
            v_day_121_wait_q = 'WL Cleared'
            v_day_121_text = 'WL Cleared'
        if len(v_eve_121_waiting) > 0:
            v_eve_121_wait_q =round(v_eve_121_waiting['Wait time'].sum()/
                                    len(v_eve_121_waiting.index),1)
            v_eve_121_text = f"average wait {v_eve_121_wait_q} weeks"
        else:
            v_eve_121_wait_q = 'WL Cleared'
            v_eve_121_text = 'WL Cleared'

        if len(IESO_waiting) > 0:
            IESO_wait_q = round(IESO_waiting['Wait time'].sum()/
                                len(IESO_waiting.index),1)
            IESO_delta_text = f"average wait {IESO_wait_q} weeks"
        else:
            IESO_delta = 'WL Cleared'
            IESO_delta_text = 'WL Cleared'

        if len(v_day_group_waiting) > 0:
            v_day_group_wait_q = round(v_day_group_waiting['Wait time'].sum()/
                                   len(v_day_group_waiting.index),1)
            v_day_group_text = f"average wait {v_day_group_wait_q} weeks"
        else:
            v_day_group_wait_q = 'WL Cleared'
            v_day_group_text = 'WL Cleared'
        if len(v_eve_group_waiting) > 0:
            v_eve_group_wait_q = round(v_eve_group_waiting['Wait time'].sum()/
                                       len(v_eve_group_waiting.index),1)
            v_eve_group_text = f"average wait {v_eve_group_wait_q} weeks"
        else:
            v_eve_group_wait_q = 'WL Cleared'
            v_eve_group_text = 'WL Cleared'


    st.markdown('##')
    st.subheader('Trend Graphs')
    st.markdown('##')

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📈 IESO", "📈 121 F2F Day",'📈 121 Virtual Day','📈 121 F2F Eve','📈 121 Virtual Eve', '📈 Group Day','📈 Group Eve'])
    #ata = np.random.randn(10, 1)

    #tab1.subheader("A tab with a chart")
    #tab1.line_chart(data)

    tab1.write('IESO Waiting list numbers')
    tab1.line_chart(IESO_timeline)
    tab2.write('121 Face to Face Daytime Waiting list numbers')
    tab2.line_chart(a121_F2F_day_timeline)
    tab3.write('121 Virtual Daytime Waiting list numbers')
    tab3.line_chart(a121_virtual_day_timeline)
    tab4.write('121 Face to Face Evening Waiting list numbers')
    tab4.line_chart(a121_F2F_eve_timeline)
    tab5.write('121 Virtual Evening Waiting list numbers')
    tab5.line_chart(a121_virtual_eve_timeline)
    tab6.write('Group Daytime Waiting list numbers')
    tab6.line_chart(Group_timeline_day)
    tab7.write('Group Evening Waiting list numbers')
    tab7.line_chart(Group_timeline_eve)

    F2F_Day_121_w = col1.metric(label = '121 F2F Day patients waiting', 
                                value = F2F_day_121_text)
    F2F_Eve_121_w = col2.metric(label = '121 F2F Eve patients waiting', 
                                value = F2F_eve_121_text)
    v_Day_121_w = col3.metric(label = '121 Virtual Day patients waiting', 
                              value = v_day_121_text)
    v_Eve_121_w_ = col4.metric(label = '121 Virtual Eve patients waiting', 
                               value = v_eve_121_text)
    IESO_w = col1.metric(label = 'IESO patients waiting', 
                         value = IESO_delta_text)
    v_day_Group_w = col2.metric(label = 'Group Virtual Day patients waiting', 
                                value = v_day_group_text)
    v_eve_Group_w = col3.metric(label = 'Group Eve patients waiting', 
                                value = v_eve_group_text)

    st.markdown('##')

    st.markdown('##')
    #with st.expander('Data Tables'):
    st.subheader('Data Tables')
    st.write('Table of waiting referrals')
    tab11, tab12, tab13, tab14, tab15, tab16, tab17 = st.tabs([
        "🗃 IESO", "🗃 121 F2F Day",'🗃 121 Virtual Day','🗃 121 F2F Eve',
        '🗃 121 Virtual Eve', '🗃 Group Day','🗃 Group Eve'])

    st.write('Table of complete referrals')
    tab21, tab22, tab23, tab24, tab25, tab26, tab27 = st.tabs([
        "🗃 IESO", "🗃 121 F2F Day",'🗃 121 Virtual Day','🗃 121 F2F Eve',
        '🗃 121 Virtual Eve', '🗃 Group Day','🗃 Group Eve'])

    tab21.write('IESO complete')
    tab21.dataframe(IESO_complete)
    tab11.write('IESO waiting')
    tab11.dataframe(IESO_waiting)
    tab22.write('121 Face to face day complete') 
    tab22.dataframe(F2F_day_121_complete)
    tab12.write('121 Face to face day waiting')
    tab12.dataframe(F2F_day_121_waiting)
    tab23.write('121 face to face evening complete') 
    tab23.dataframe(F2F_eve_121_complete)
    tab13.write('121 face to face evening waiting')
    tab13.dataframe(F2F_eve_121_waiting)
    tab24.write('121 virtual evening complete')
    tab24.dataframe(v_eve_121_complete)
    tab14.write('121 virtual evening waiting')
    tab14.dataframe(v_eve_121_waiting)
    tab25.write('121 Virtual evening complete') 
    tab25.dataframe(v_eve_121_complete)
    tab15.write('121 Virtual eve waiting')
    tab15.dataframe(v_eve_121_waiting)
    tab26.write('Group virtual day complete')
    tab26.dataframe(v_day_group_complete)
    tab16.write('Group virtual day waiting')
    tab16.dataframe(v_day_group_waiting)
    tab27.write('Group virtual evening complete')
    tab27.dataframe(v_eve_group_complete)
    tab17.write('Group virtual evening waiting')
    tab17.dataframe(v_eve_group_waiting)
