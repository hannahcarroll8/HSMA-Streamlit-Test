# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 15:50:37 2022

@author: hannah.carroll
"""

import simpy
import random
import pandas as pd
import numpy as np
#import data_reader
import streamlit as st

class g:
    with st.sidebar:
        mean_new = st.number_input("Mean number of new patients per week", 
                                   min_value=0.0, max_value=200.0, value=44.29)
        prob_prefer_eve = st.number_input("Probability a patient will prefer " 
                                          "evening appointments", 
                                          min_value = 0.00, max_value=1.00, 
                                          value=0.133)
        prob_prefer_f2f = st.number_input("Probability a patient will prefer "
                                          "face to face appointments", 
                                          min_value = 0.00, max_value=1.00, 
                                          value=0.208)
        prob_priority = st.number_input("Probability a patient will be a "
                                        "priority patient", min_value = 0.0, 
                                        max_value=1.0, value=0.14)
        prob_refer_ieso = st.number_input("Probability a patient will be "
                                          "referred to IESO", min_value = 0.0, 
                                          max_value=1.0, value=0.18)
        prob_refer_121 = st.number_input("Probability a patient will be "
                                         "referred to 121", min_value = 0.0, 
                                         max_value=1.0, value=0.63)
        prob_refer_group = st.number_input("Probability a patient will be "
                                           "referred to group",min_value = 0.0, 
                                           max_value=1.0, value=0.19)
        mean_wait_ieso = st.number_input("Mean number of weeks patients wait "
                                         "for IESO", min_value = 0.0, 
                                         max_value = 52.0,value = 5.93)
        sess_no_group = st.number_input("(Mean) number of sessions for a full "
                                        "course of group therapy", 
                                        min_value = 1, max_value = 25, 
                                        value = 12)
        mean_sess_no_121 = st.number_input("Mean number of sessions patients "
                                           "undertake for 121", min_value = 1, 
                                           max_value = 30, value = 13)
        mean_sess_no_ieso = st.number_input("Mean number of sessions patients "
                                            "undertake for IESO", 
                                            min_value = 1.0, max_value = 30.0, 
                                            value = 9.41)
        num_group_spaces_v = st.number_input("Number of spaces available on "
                                             "each virtual group", 
                                             min_value = 0, max_value = 20, 
                                             value = 6)
        num_group_spaces_f2f = st.number_input("Number of spaces available on "
                                               "each F2F group", min_value = 0, 
                                               max_value = 20, value = 0)
        num_v_eve_groups = st.number_input("Number of virtual evening groups "
                                           "running per week", min_value = 0, 
                                           max_value = 30, value = 4)
        num_v_day_groups = st.number_input("Number of virtual daytime groups "
                                           "running per week", min_value = 0, 
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
                                              "week", min_value = 0, 
                                              max_value = 30, value = 12)
        num_app_121_v_eve = st.number_input("Number of evening virtual 121 "
                                            "appointments available per week", 
                                            min_value = 0, max_value = 100, 
                                            value = 44)
        num_app_121_f2f_day = st.number_input("Number of daytime face to face "
                                              "121 appointments available per "
                                              "week", min_value = 0, 
                                              max_value = 400, value = 77)
        num_app_121_v_day = st.number_input("Number of daytime virtual "
                                            "appointments available per week", 
                                            min_value = 0, max_value = 400, 
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
    completed_df["Wait time"] = []
    completed_df["Stage"] = []
    completed_df["No of Appts"] = []
    completed_df.set_index("P_ID", inplace=True)
    
    duration = 10
    num_runs = 1
    warm_up = 10
    sim_duration = warm_up + duration

class Patient:
    def __init__(self, p_id):
        self.p_id = p_id
        self.q_start = 0
        self.q_end = 0
        self.wait_time = 0
        self.appointments = 0
        self.eve_prefer = False
        self.f2f_prefer = False
        x = random.random()
        
        #What treatment are they referred to?
        if x < g.prob_refer_ieso:
            self.treatment = "IESO"
        if g.prob_refer_ieso <=x< (g.prob_refer_ieso + g.prob_refer_121):
            self.treatment = "121"
        if (g.prob_refer_ieso + g.prob_refer_121) <= x:
            self.treatment = "Group"
        
        #is this a priority patient?
        if x < g.prob_priority:
            self.priority = 0
        else:
            self.priority = 1

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
    
    #Patients join the system once they have had their assessment or review     
    def generate_patients(self):
        while True:
            self.patient_counter += 1
            p = Patient(self.patient_counter)
            p.q_start = self.env.now
            
            x=random.random()
            #does patient prefer evening appointments? 
            #(group & 121 patients only)
            if p.treatment == "121" or p.treatment == "Group":
                if x < g.prob_prefer_eve:
                    p.eve_prefer = True
                else:
                    p.eve_prefer = False
       
            #does patient prefer F2F appointments? (121 patients)
            if p.treatment=="121" and (g.num_app_121_f2f_eve>0 or
                                                      g.num_app_121_f2f_day>0):
                if x < g.prob_prefer_f2f:
                    p.f2f_prefer = True
                else:
                    p.f2f_prefer = False
        
            #does patient prefer F2F appointments? (group patients)
            if p.treatment == "Group" and (g.num_app_group_f2f_eve>0 or
                                                    g.num_app_group_f2f_day>0):
                if x < g.prob_prefer_f2f:
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
    
    #May need to set a limit on how long IESO can wait
        
    def attend_ieso(self, p):
        #As ieso is unlimited, sample wait time based on mean
        sampled_ieso_wait = random.expovariate(1.0 / g.mean_wait_ieso)
        #wait for that time
        yield self.env.timeout(sampled_ieso_wait)
            
        #grab an ieso appointment
        with self.ieso.request(priority=p.priority) as req:
            yield req
            #calculate the patient's wait time and add to dataframe
            p.q_end = self.env.now
            p.wait_time     = p.q_end - p.q_start
            #sample the number of appointments patient will attend
            p.appointments = int(random.expovariate(1.0 / 
                                                         g.mean_sess_no_ieso))
            
            #Remove patient from queue DF
            g.current_q_df = g.current_q_df.drop(p.p_id)
            
            #Append patient info to completed DF (post warm up only)
            if self.env.now > g.warm_up:
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                          "Evening Appt?":[p.eve_prefer],
                                          "Need F2F?":[p.f2f_prefer],
                                          "Priority Patient?":[p.priority],
                                          "Wait time":[p.wait_time],
                                          "Stage":[p.treatment],
                                          "No of Appts":[p.appointments]})
                df_to_add.set_index("P_ID", inplace=True)
                g.completed_df = g.completed_df.append(df_to_add)
            
            #hold the appointment for the sampled number of weeks
            yield self.env.timeout(p.appointments)
        #Exit point
        
    def attend_121(self, p):
        #Request the relevant appointment and wait until one is available
        if p.eve_prefer == True and p.f2f_prefer == True:
            with self.app_121_f2f_eve.request(priority=p.priority) as req:
                yield req
                
                #End and calculate the wait time and add to dataframe
                p.q_end = self.env.now
                p.wait_time = p.q_end - p.q_start
                
                #Sample the number of appointments patient will attend
                p.appointments = int(random.expovariate(1.0/g.mean_sess_no_121))
                
                #Remove patient from queue DF
                g.current_q_df = g.current_q_df.drop(p.p_id)
                
                #Append patient info to completed df (post warm up only)
                if self.env.now > g.warm_up:
                    df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                          "Evening Appt?":[p.eve_prefer],
                                          "Need F2F?":[p.f2f_prefer],
                                          "Priority Patient?":[p.priority],
                                          "Wait time":np.round(
                                              [p.wait_time],2),
                                          "Stage":[p.treatment],
                                          "No of Appts":[p.appointments]})
                    df_to_add.set_index("P_ID", inplace=True)
                    g.completed_df = g.completed_df.append(df_to_add)
                
                #Hold for sampled number of weeks
                yield self.env.timeout(p.appointments)
                #Exit point
                
        elif p.eve_prefer == True and p.f2f_prefer == False:
            with self.app_121_v_eve.request(priority=p.priority) as req:
                yield req
                #End and calculate the wait time and add to dataframe
                p.q_end = self.env.now
                p.wait_time = p.q_end - p.q_start
                
                #Sample the number of appointments patient will attend
                p.appointments = int(random.expovariate(
                    1.0/g.mean_sess_no_121))
                
                #Remove patient from queue DF
                g.current_q_df = g.current_q_df.drop(p.p_id)
                
                #Append patient info to df (post warm up only)
                if self.env.now > g.warm_up:
                    df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                              "Evening Appt?":[p.eve_prefer],
                                              "Need F2F?":[p.f2f_prefer],
                                              "Priority Patient?":[p.priority],
                                              "Wait time":np.round(
                                                  [p.wait_time],2),
                                              "Stage":[p.treatment],
                                              "No of Appts":[
                                                  p.appointments]})
                    df_to_add.set_index("P_ID", inplace=True)
                    g.completed_df = g.completed_df.append(df_to_add)
                
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
                p.appointments = int(random.expovariate(1.0/g.mean_sess_no_121))
                
                #Remove patient from queue DF
                g.current_q_df = g.current_q_df.drop(p.p_id)
                
                #Append patient info to df (post warm up only)
                if self.env.now > g.warm_up:
                    df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                          "Evening Appt?":[p.eve_prefer],
                                          "Need F2F?":[p.f2f_prefer],
                                          "Priority Patient?":[p.priority],
                                          "Wait time":np.round(
                                              [p.wait_time],2),
                                          "Stage":[p.treatment],
                                          "No of Appts":[p.appointments]})
                    df_to_add.set_index("P_ID", inplace=True)
                    g.completed_df = g.completed_df.append(df_to_add)
                
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
                p.appointments = int(random.expovariate(1.0/g.mean_sess_no_121))
                
                #Remove patient from queue DF
                g.current_q_df = g.current_q_df.drop(p.p_id)
                
                #Append patient info to df (post warm up only)
                if self.env.now > g.warm_up:
                    df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                              "Evening Appt?":[p.eve_prefer],
                                              "Need F2F?":[p.f2f_prefer],
                                              "Priority Patient?":[p.priority],
                                              "Wait time":np.round(
                                                  [p.wait_time],2),
                                              "Stage":[p.treatment],
                                              "No of Appts":[p.appointments]})
                    df_to_add.set_index("P_ID", inplace=True)
                    g.completed_df = g.completed_df.append(df_to_add)
                
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
                    
                    #Remove patient from queue DF
                    g.current_q_df = g.current_q_df.drop(p.p_id)
                    
                    #Append patient info to completed df (post warm up only)
                    if self.env.now > g.warm_up:
                        df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                              "Evening Appt?":[p.eve_prefer],
                                              "Need F2F?":[p.f2f_prefer],
                                              "Priority Patient?":[p.priority],
                                              "Wait time":[p.wait_time],
                                              "Stage":[p.treatment],
                                              "No of Appts":[p.appointments]})
                        df_to_add.set_index("P_ID", inplace=True)
                        g.completed_df = g.completed_df.append(df_to_add)
                    
                    #Hold for the specified number of weeks
                    yield self.env.timeout(g.sess_no_group)
                    #Exit point
        elif g.num_F2F_day_groups > 0:
            if p.eve_prefer == False and p.f2f_prefer == True:
                with self.app_group_f2f_day.request(priority=p.priority) as req:
                    yield req
                    
                    #Calculate wait time
                    p.q_end = self.env.now
                    p.wait_time = p.q_end - p.q_start
                    
                    #Remove patient from queue DF
                    g.current_q_df = g.current_q_df.drop(p.p_id)
                    
                    #Append patient info to completed df (post warm up only)
                    if self.env.now > g.warm_up:
                        df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                              "Evening Appt?":[p.eve_prefer],
                                              "Need F2F?":[p.f2f_prefer],
                                              "Priority Patient?":[p.priority],
                                              "Wait time":[p.wait_time],
                                              "Stage":[p.treatment],
                                              "No of Appts":[p.appointments]})
                        df_to_add.set_index("P_ID", inplace=True)
                        g.completed_df = g.completed_df.append(df_to_add)
                    
                    #Hold for the specified number of weeks
                    yield self.env.timeout(g.sess_no_group)
                    #Exit point
        elif p.eve_prefer == True and p.f2f_prefer == False:
            with self.app_group_v_eve.request(priority=p.priority) as req:
                yield req
                    
                #Calculate wait time
                p.q_end = self.env.now
                p.wait_time = p.q_end - p.q_start
                    
                #Remove patient from queue DF
                g.current_q_df = g.current_q_df.drop(p.p_id)
                
                #Append patient info to completed df (post warm up only)
                if self.env.now > g.warm_up:
                    df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                          "Evening Appt?":[p.eve_prefer],
                                          "Need F2F?":[p.f2f_prefer],
                                          "Priority Patient?":[p.priority],
                                          "Wait time":[p.wait_time],
                                          "Stage":[p.treatment],
                                          "No of Appts":[p.appointments]})
                    df_to_add.set_index("P_ID", inplace=True)
                    g.completed_df = g.completed_df.append(df_to_add)
                
                #Hold for the specified number of weeks
                yield self.env.timeout(g.sess_no_group)
                #Exit point                
        elif p.eve_prefer == False and p.f2f_prefer == False:
            with self.app_group_v_day.request(priority=p.priority) as req:
                    yield req
                    
                    #Calculate wait time
                    p.q_end = self.env.now
                    p.wait_time = p.q_end - p.q_start
                    
                    #Remove patient from queue DF
                    g.current_q_df = g.current_q_df.drop(p.p_id)
                    
                    #Append patient info to completed df (post warm up only)
                    if self.env.now > g.warm_up:
                        df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                              "Evening Appt?":[p.eve_prefer],
                                              "Need F2F?":[p.f2f_prefer],
                                              "Priority Patient?":[p.priority],
                                              "Wait time":[p.wait_time],
                                              "Stage":[p.treatment],
                                              "No of Appts":[p.appointments]})
                        df_to_add.set_index("P_ID", inplace=True)
                        g.completed_df = g.completed_df.append(df_to_add)
                    
                    #Hold for the specified number of weeks
                    yield self.env.timeout(g.sess_no_group)
                    #Exit point
        
    def run(self):
        self.env.process(self.generate_patients())
        self.env.run(until=g.sim_duration)

st.title("Steps 2 Wellbeing Discrete Event Simulation") 
"Please set your parameters on the left hand side, then press Run"       
if st.button("Run"):
    for run in range(g.num_runs):
        model = Step_3_Model()
        model.run()
        #model.results_df.to_csv(f"DES_Model_Results{run+1}.csv")
        #data_reader.stats(f"DES_Model_Results{run+1}.csv", run+1)
    
    #Calculate wait times for current queue
    g.current_q_df["Started Queueing"] = g.sim_duration - g.current_q_df[
                                                            "Started Queueing"]
    g.current_q_df.rename(columns={"Started Queueing":"Wait time"}, 
                                                                  inplace=True)
    
    #Stats
    wait_all_stats = g.completed_df["Wait time"].describe()
    wait_all_stats = wait_all_stats.to_frame()
    wait_all_stats = wait_all_stats.T
    wait_all_stats = wait_all_stats.round(2)
    
    wait_by_treatment_stats = g.completed_df[["Stage", "Wait time"]].groupby(
                                                           "Stage").describe()
    wait_by_treatment_stats.columns=wait_by_treatment_stats.columns.droplevel(-2)
    
    wait_by_evening_stats = g.completed_df[["Evening Appt?", 
                             "Wait time"]].groupby("Evening Appt?").describe()
    wait_by_evening_stats.rename(index={0.0:'Daytime', 1.0:'Evening'}, 
                                 inplace=True)
    wait_by_evening_stats.columns = wait_by_evening_stats.columns.droplevel(-2)
    
    wait_by_f2f_stats = g.completed_df[["Need F2F?", 
                              "Wait time"]].groupby("Need F2F?").describe()
    wait_by_f2f_stats.rename(index={0.0:'Virtual', 1.0:'F2F'}, inplace=True)
    wait_by_f2f_stats.columns = wait_by_f2f_stats.columns.droplevel(-2)
    
    
    wait_by_priority_stats = g.completed_df[["Priority Patient?", 
                                "Wait time"]].groupby(
                                    "Priority Patient?").describe()
    wait_by_priority_stats.rename(index={0.0:'Priority', 1.0:'Not Priority'}, 
                                  inplace=True)
    wait_by_priority_stats.columns = wait_by_priority_stats.columns.droplevel(-2)
    
    #write to streamlit
    st.header("Raw Data")
    st.write("Full list of patients who have finished queueing (being treated"
             " or have been discharged)")
    st.write(g.completed_df)
    "Current wait list"
    st.write(g.current_q_df)
    
    st.header("Statistics For Patients Who Have Finished Queueing")
    "Wait time statistics across all patients"
    st.metric(label="Total Patients", value=int(wait_all_stats["count"]))
    st.metric(label="Mean Wait Time", value=round(wait_all_stats["mean"], 2))
    st.write(wait_all_stats.style.format("{:.2f}"))
    "Wait time statistics by treatment type"
    st.metric(label="IESO Mean Wait Time", 
              value=round(wait_by_treatment_stats.at["IESO","mean"], 2))
    st.metric(label="Group Mean Wait Time", 
              value=round(wait_by_treatment_stats.at["Group","mean"], 2))
    st.metric(label="121 Mean Wait Time", 
              value=round(wait_by_treatment_stats.at["121","mean"], 2))
    st.write(wait_by_treatment_stats.style.format("{:.2f}"))
    "Wait time statistics by daytime/evening preference"
    st.metric(label="Daytime Mean Wait Time", 
              value=round(wait_by_evening_stats.at["Daytime","mean"], 2))
    st.metric(label="Evening Mean Wait Time", 
              value=round(wait_by_evening_stats.at["Evening","mean"], 2))
    st.write(wait_by_evening_stats.style.format("{:.2f}"))
    "Wait time statistics by face to face/virtual preference"
    st.metric(label="Face to Face Mean Wait Time", 
              value=round(wait_by_f2f_stats.at["F2F","mean"], 2))
    st.metric(label="Virtual Mean Wait Time", 
              value=round(wait_by_f2f_stats.at["Virtual","mean"], 2))
    st.write(wait_by_f2f_stats.style.format("{:.2f}"))
    "Wait time statistics by priority/non-priority"
    st.metric(label="Priority Mean Wait Time", 
              value=round(wait_by_priority_stats.at["Priority","mean"], 2))
    st.metric(label="Non-Priority Mean Wait Time", 
              value=round(wait_by_priority_stats.at["Not Priority","mean"], 2))
    st.write(wait_by_priority_stats.style.format("{:.2f}"))
