# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import simpy
import random
import pandas as pd
import numpy as np
#import data_reader
import streamlit as st
import os

class g:
    #image1 = os.path.abspath('DiiSnew.jpg')
    #image2 = os.path.abspath('Steps2wellbeing.jpg')
    st.set_page_config(layout="wide")
    #col21, col22, col23 = st.columns(3)
    #col21.image(image1)
    #col23.image(image2)

    st.markdown('##')
    #st.header('ZZZ*****This model is a test model*****ZZZ')
    st.header('Steps 2 DES')
    st.sidebar.subheader('Change referrals and preferences here')
    mean_new = st.sidebar.slider("Ave number of referred patients per week",0,100,44) #mean new patients per week
    inter_arrival = 1/mean_new
    mean_wait_ieso = 5.9#st.sidebar.slider("Mean weeks to wait for IESO",0.0,12.0,5.9) #mean number of weeks patients wait for ieso
    slider_prob_prefer_eve = st.sidebar.slider("% Patients with an evening preference",0,100,13) #prob a patient will prefer evening appointments
    slider_prob_prefer_f2f = st.sidebar.slider("% Patients with an face to face preference",0,100,21) #prob a patient will prefer f2f appointments
    slider_prob_priority = st.sidebar.slider("% Patients with a prioirty",0,100,14) #prob a patient will be a priority patient
    slider_prob_refer_ieso = st.sidebar.slider("% Patients who are referred to IESO",0,100,18) #prob patient will be referred to ieso
    slider_prob_refer_121 = st.sidebar.slider("% Patients who are referred to 121 session",0,100,63) #prob patient will be referred to 121
    slider_prob_refer_group = st.sidebar.slider("% Patients who are referred to a group session",0,100,19)
    
    
    prob_prefer_eve = slider_prob_prefer_eve/100 #prob a patient will prefer evening appointments
    prob_prefer_f2f = slider_prob_prefer_f2f/100 #prob a patient will prefer f2f appointments
    prob_priority = slider_prob_priority/100 #prob a patient will be a priority patient
    prob_refer_ieso = slider_prob_refer_ieso/100 #prob patient will be referred to ieso
    prob_refer_121 = slider_prob_refer_121/100 #prob patient will be referred to 121
    prob_refer_group = slider_prob_refer_group/100 #prob patient will be referred to group
    #ieso_do = #prob patient will drop out of IESO
    #121_do = #prob patient will drop out of 121
    #group_do = #prob patient will drop out of group
    #mean_wait_ieso = st.sidebar.number_input("Mean weeks to wait for IESO",0.0,12.0,5.9) #mean number of weeks patients wait for ieso
    
    #set streamlit interactive widgets

    st.subheader('Enter number of available appointments & group size here')
    col11,col12,col13,col14 = st.columns (4)

    num_app_121_f2f_eve = col12.slider('''Number of Face-to-Face 121 Evening 
            appointments p/w''',
            1,50,8, key=3) #num evening F2F 121 appointments available /week ##12
    num_app_121_v_eve = col14.slider('''Number of Virtual 121 Evening 
            appointments p/w''',
         1,100,30, key=4) #num evening virtual 121 appointments available /week ##44
    num_app_121_f2f_day = col11.slider('''Number of Face-to-Face 121 Daytime 
            appointments p/w''',
        1,200,55, key=5)  #num daytime F2F 121 appointments available /week ##77
    num_app_121_v_day = col13.slider('''Number of Virtual 121 Daytime 
            appointments p/w''',
        1,500,215, key=6) #num daytime virtual 121 appointments available /week ##293
    sess_no_group = col11.slider('Average Number of Clients in a group',6,18,12, key=0) 
            #number of sessions patients undertake for group therapy
    mean_sess_no_121 = 13.03 #mean num sessions patients take for 121 therapy
    mean_sess_no_ieso = 9.41 #mean num sessions patients undertake for ieso
    num_app_ieso = 9999999 #unlimited number of ieso appointments
    num_app_group_eve = col13.slider('Number of Group Evening appointments p/w',
            1,50,11, key=1) #num evening group appointments available per week ##48
    num_app_group_day = col12.slider('Number of Group Daytime appointments p/w',
            1,200,77, key=2)  #num daytime group appointments available per week ##174
    sim_duration = 78
    num_runs = 1
    warm_up = 26

class Patient:
    def __init__(self, p_id):
        self.p_id = p_id
        self.q_start = 0
        self.q_end = 0
        self.wait_time = 0
        x = random.random()
        y = random.random()
        z = random.random()
        #does patient prefer evening appointments?
        if x < g.prob_prefer_eve:
            self.eve_prefer = 0
        else:
            self.eve_prefer = 1
        #does patient prefer F2F appointments?
        if y < g.prob_prefer_f2f:
            self.f2f_prefer = 0
        else:
            self.f2f_prefer = 1
        #is this a priority patient?
        if z < g.prob_priority:
            self.priority = 0
        else:
            self.priority = 1

class Step_3_Model:
    def __init__(self):
        self.env = simpy.Environment()
        self.patient_counter = 0
        self.results_df = pd.DataFrame()
        self.results_df["P_ID"] = []
        #self.results_df["Evening Appt?"] = []
        #self.results_df["Priority Patient?"] = []
        #self.results_df["Need F2F?"] = []
        self.results_df["Wait time"] = []
        #self.results_df["Stage"] = []
        self.results_df["No of Appts"] = []
        self.results_df.set_index("P_ID", inplace=True)
        
        # sceond dataframe to report on patients as they are allocated a service
        self.referral_df = pd.DataFrame()
        self.referral_df["P_ID"] = []
        self.referral_df["Referred_to"] =[]
        self.referral_df.set_index("P_ID", inplace = True)
        
        self.ieso = simpy.PriorityResource(self.env, capacity=g.num_app_ieso) 
                                                                #IESO
        self.app_group_eve = simpy.PriorityResource(self.env, 
                                            capacity=g.num_app_group_eve)
                                                    #group evening appointments
        self.app_group_day = simpy.PriorityResource(self.env, 
                                            capacity=g.num_app_group_day) 
                                                    #group daytime appointments
        #self.app_group_f2f = simpy.PriorityResource #group F2F appointments
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
            print(f"Patient {p.p_id} generated")
                        
            x = random.random()
            if x < g.prob_refer_ieso:
                print (f"Patient {p.p_id} has been referred to IESO")
                p.q_start = self.env.now
                self.env.process(self.attend_ieso(p))
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                          "Referred_to" : ["IESO"],
                                         "Evening Appt?":[p.eve_prefer],
                                         "Need F2F?":[p.f2f_prefer],
                                         "Priority Patient?":[p.priority],
                                         'Started Queuing':[p.q_start]})
                df_to_add.set_index("P_ID", inplace = True)
                self.referral_df = self.referral_df.append(df_to_add)
            elif g.prob_refer_ieso <=x< (g.prob_refer_ieso + g.prob_refer_121):
                print (f"Patient {p.p_id} has been referred to 121 therapy")
                p.q_start = self.env.now
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                          "Referred_to" : ["121"],
                                          "Evening Appt?":[p.eve_prefer],
                                           "Need F2F?":[p.f2f_prefer],
                                           "Priority Patient?":[p.priority],
                                           'Started Queuing':[p.q_start]})
                df_to_add.set_index("P_ID", inplace = True)
                self.referral_df = self.referral_df.append(df_to_add)
                print(f"Patient {p.p_id} started queueing at week "
                      f"{p.q_start:.2f}")
                self.env.process(self.attend_121(p))
            elif (g.prob_refer_ieso + g.prob_refer_121) <= x:
                print (f"Patient {p.p_id} has been referred to group therapy")
                p.q_start = self.env.now
                print(f"Patient {p.p_id} started queueing at week "
                      f"{p.q_start:.2f}")
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                          "Referred_to" : ["Group"],
                                          "Evening Appt?":[p.eve_prefer],
                                          "Need F2F?":[p.f2f_prefer],
                                          "Priority Patient?":[p.priority],
                                          'Started Queuing':[p.q_start]})
                df_to_add.set_index("P_ID", inplace = True)
                self.referral_df = self.referral_df.append(df_to_add)
                self.env.process(self.attend_group(p))
            else:
                print ("Error - referral process")
            
            sampled_interarrival = random.expovariate(1.0 / g.inter_arrival)
            yield self.env.timeout(sampled_interarrival)
        
    #after being referred, patients wait for an appointment to become available
    #then use that appointment for a certain number of weeks
        
    def attend_ieso(self, p):
        #As ieso is unlimited, sample wait time based on mean
        sampled_ieso_wait = random.expovariate(1.0 / g.mean_wait_ieso)
        #print(sampled_ieso_wait)
        #wait for that time
        yield self.env.timeout(sampled_ieso_wait)
            
        #grab an ieso appointment
        with self.ieso.request(priority=p.priority) as req:
            yield req
            #calculate the patient's wait time and add to dataframe
            p.q_end = self.env.now
            #print(p.q_end)
            p.wait_time += (p.q_end - p.q_start)
            print(f"Patient {p.p_id} waited for IESO for {p.wait_time:.2f} "
                  f"weeks")
            #sample the number of appointments patient will attend
            sample_ieso_appoint = int(random.expovariate(1.0 / 
                                                         g.mean_sess_no_ieso))
            #Append patient info to df (post warm up only)
            #if self.env.now > g.warm_up:
            df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                     # "Evening Appt?":[p.eve_prefer],
                                     # "Need F2F?":[p.f2f_prefer],
                                     # "Priority Patient?":[p.priority],
                                      "Wait time":np.round(
                                          [p.wait_time],2),
                                      #"Stage":["IESO"],
                                      "No of Appts":[sample_ieso_appoint]})
            df_to_add.set_index("P_ID", inplace=True)
            self.results_df = self.results_df.append(df_to_add)
            
            #hold the appointment for the sampled number of weeks
            yield self.env.timeout(sample_ieso_appoint)
        #Exit point
        
    def attend_121(self, p):
        #Request the relevant appointment and wait until one is available
        if p.eve_prefer == False and p.f2f_prefer == False:
            with self.app_121_f2f_eve.request(priority=p.priority) as req:
                yield req
                
                #End and calculate the wait time and add to dataframe
                p.q_end = self.env.now
                p.wait_time = p.wait_time + (p.q_end - p.q_start)
                print(f"Patient {p.p_id} waited for evening F2F 121 for "
                      f"{p.wait_time:.2f} weeks")
                
                #Sample the number of appointments patient will attend
                sample_121_appoint = int(random.expovariate(
                    1.0/g.mean_sess_no_121))
                
                #Append patient info to df (post warm up only)
                #if self.env.now > g.warm_up:
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                      #"Evening Appt?":[p.eve_prefer],
                                      #"Need F2F?":[p.f2f_prefer],
                                      #"Priority Patient?":[p.priority],
                                      "Wait time":np.round(
                                          [p.wait_time],2),
                                     #"Stage":["121"],
                                      "No of Appts":[sample_121_appoint]})
                df_to_add.set_index("P_ID", inplace=True)
                self.results_df = self.results_df.append(df_to_add)
                
                #Hold for sampled number of weeks
                yield self.env.timeout(sample_121_appoint)
            #Exit point
                
        elif p.eve_prefer == False and p.f2f_prefer == True:
            with self.app_121_v_eve.request(priority=p.priority) as req:
                yield req
                #End and calculate the wait time and add to dataframe
                p.q_end = self.env.now
                p.wait_time = p.wait_time + (p.q_end - p.q_start)
                print(f"Patient {p.p_id} waited for evening virtual 121 for "
                      f"{p.wait_time:.2f} weeks")
                
                #Sample the number of appointments patient will attend
                sample_121_appoint = int(random.expovariate(
                    1.0/g.mean_sess_no_121))
                
                #Append patient info to df (post warm up only)
                #if self.env.now > g.warm_up:
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                          #"Evening Appt?":[p.eve_prefer],
                                         # "Need F2F?":[p.f2f_prefer],
                                          #"Priority Patient?":[p.priority],
                                          "Wait time":np.round(
                                              [p.wait_time],2),
                                          #"Stage":["121"],
                                          "No of Appts":[
                                              sample_121_appoint]})
                df_to_add.set_index("P_ID", inplace=True)
                self.results_df = self.results_df.append(df_to_add)
                
                #Hold for sampled number of weeks
                yield self.env.timeout(sample_121_appoint)
                #Exit point
                
        elif p.eve_prefer == True and p.f2f_prefer == False:
            with self.app_121_f2f_day.request(priority=p.priority) as req:
                yield req
                p.q_end = self.env.now
                
                #Calculate wait time
                p.wait_time = p.wait_time + (p.q_end - p.q_start)
                print(f"Patient {p.p_id} waited for daytime F2F 121 for "
                      f"{p.wait_time:.2f} weeks")
                
                #Sample the number of appointments patient will attend
                sample_121_appoint = int(random.expovariate(
                    1.0/g.mean_sess_no_121))
                
                #Append patient info to df (post warm up only)
                #if self.env.now > g.warm_up:
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                      #"Evening Appt?":[p.eve_prefer],
                                      #"Need F2F?":[p.f2f_prefer],
                                      #"Priority Patient?":[p.priority],
                                      "Wait time":np.round(
                                          [p.wait_time],2),
                                      #"Stage":["121"],
                                      "No of Appts":[sample_121_appoint]})
                df_to_add.set_index("P_ID", inplace=True)
                self.results_df = self.results_df.append(df_to_add)
            
                #Hold for sampled number of weeks
                yield self.env.timeout(sample_121_appoint)
                #Exit point
                
        elif p.eve_prefer == True and p.f2f_prefer == True:
            with self.app_121_v_day.request(priority=p.priority) as req:
                yield req
                
                #Calculate wait time
                p.q_end = self.env.now
                p.wait_time = p.wait_time + (p.q_end - p.q_start)
                print(f"Patient {p.p_id} waited for daytime virtual 121 for "
                      f" {p.wait_time:.2f} weeks")
                
                #Sample the number of appointments patient will attend
                sample_121_appoint = int(random.expovariate(
                    1.0/g.mean_sess_no_121))
                
                #Append patient info to df (post warm up only)
                #if self.env.now > g.warm_up:
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                         # "Evening Appt?":[p.eve_prefer],
                                         # "Need F2F?":[p.f2f_prefer],
                                          #"Priority Patient?":[p.priority],
                                          "Wait time":np.round(
                                              [p.wait_time],2),
                                          #"Stage":["121"],
                                          "No of Appts":[
                                              sample_121_appoint]})
                df_to_add.set_index("P_ID", inplace=True)
                self.results_df = self.results_df.append(df_to_add)
                
                #Hold for sampled number of weeks
                yield self.env.timeout(sample_121_appoint)
                #Exit point
        else:
            print ("Error - 121 appointment allocation process")
        
    def attend_group(self, p):
        #Request the relevant appointment and wait until one is available
        if p.eve_prefer == False:
            with self.app_group_eve.request(priority=p.priority) as req:
                yield req
                
                #Calculate wait time
                p.q_end = self.env.now
                p.wait_time = p.wait_time + (p.q_end - p.q_start)
                print(f"Patient {p.p_id} waited for evening virtual group "
                      f"therapy for {p.wait_time} weeks")
                
                #Append patient info to df (post warm up only)
                #if self.env.now > g.warm_up:
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                      #"Evening Appt?":[p.eve_prefer],
                                      #"Need F2F?":[p.f2f_prefer],
                                      #"Priority Patient?":[p.priority],
                                      "Wait time":np.round(
                                          [p.wait_time],2),
                                      #"Stage":["Group"],
                                      "No of Appts":[g.sess_no_group]})
                df_to_add.set_index("P_ID", inplace=True)
                self.results_df = self.results_df.append(df_to_add)
                
                #Hold for the specified number of weeks
                yield self.env.timeout(g.sess_no_group)
                #Exit point
        elif p.eve_prefer == True:
            with self.app_group_day.request(priority=p.priority) as req:
                yield req
                
                #Calculate wait time
                p.q_end = self.env.now
                p.wait_time = p.wait_time + (p.q_end - p.q_start)
                print(f"Patient {p.p_id} waited for virtual daytime group "
                      f"therapy for {p.wait_time} weeks")
                
                #Append patient info to df (post warm up only)
                #if self.env.now > g.warm_up:
                df_to_add = pd.DataFrame({"P_ID":[p.p_id],
                                      #"Evening Appt?":[p.eve_prefer],
                                      #"Need F2F?":[p.f2f_prefer],
                                      #"Priority Patient?":[p.priority],
                                      "Wait time":np.round([p.wait_time],2),
                                      #"Stage":["Group"],
                                      "No of Appts":[g.sess_no_group]})
                df_to_add.set_index("P_ID", inplace=True)
                self.results_df = self.results_df.append(df_to_add)
                
                #Hold for the specified number of weeks
                yield self.env.timeout(g.sess_no_group)
                #Exit point
        else:
            print ("Error - Group therapy appointment allocation")
    
    
    def run(self):
        self.env.process(self.generate_patients())
        self.env.run(until=g.sim_duration)
        
for run in range(g.num_runs):
    print (f"Run {run+1} of {g.num_runs}")
    model = Step_3_Model()
    model.run()
    new_df = model.referral_df.merge(model.results_df, on='P_ID', how='outer')
    new_df['No: Weeks waiting'] = np.where(new_df['Wait time'].isna(),
                    round((g.sim_duration - new_df['Started Queuing']),2), 0)
    new_df['Evening Appt?']= new_df['Evening Appt?'].replace([0,1],[1,0])	
    new_df['Need F2F?']= new_df['Need F2F?'].replace([0,1],[1,0])	
    new_df['Priority Patient?']= new_df['Priority Patient?'].replace([0,1],
                                                                     [1,0])	
    new_df['Wait time'].replace(np.nan,0)
    new_df['End']= new_df['Started Queuing']+new_df['Wait time']+new_df['No: Weeks waiting']
    new_df.drop(new_df[new_df['End'] < 26].index, inplace = True)
    new_df.to_csv(f"Combined_Results{run+1}.csv")
    #model.results_df.to_csv(f"DES_Model_Results{run+1}.csv")
    #model.referral_df.to_csv("referral_location.csv")
  #  data_reader.stats(f"DES_Model_Results{run+1}.csv", run+1)

    IESO_df_complete = new_df[(new_df['Referred_to'].isin(['IESO'])) & 
            (new_df['End'] >= 0)]
    IESO_df_waiting = new_df[(new_df['Referred_to'].isin(['IESO'])) & 
            (new_df['End'].isnull().values)]
    F2F_day_df_complete = new_df[(new_df['Referred_to'] == '121') & 
            (new_df['End'] >= 0) & (new_df['Evening Appt?'] ==0) & 
            (new_df['Need F2F?'] ==1)]
    F2F_day_df_waiting = new_df[(new_df['Referred_to'] == '121') & 
            (new_df['End'].isnull().values) & (new_df['Evening Appt?'] ==0) &  
            (new_df['Need F2F?'] ==1)]
    F2F_eve_df_complete = new_df[(new_df['Referred_to'] == '121') & 
            (new_df['End'] >= 0) & (new_df['Evening Appt?'] ==1) & 
            (new_df['Need F2F?'] ==1)]
    F2F_eve_df_waiting = new_df[(new_df['Referred_to'] == '121') & 
            (new_df['End'].isnull().values) & (new_df['Evening Appt?'] ==1) & 
            (new_df['Need F2F?'] ==1)]
    F2F_day_df_complete_virtual = new_df[(new_df['Referred_to'] == '121') & 
            (new_df['End'] >= 0) & (new_df['Evening Appt?'] ==0) & 
            (new_df['Need F2F?'] ==0)]
    F2F_day_df_waiting_virtual = new_df[(new_df['Referred_to'] == '121') & 
            (new_df['End'].isnull().values) & (new_df['Evening Appt?'] ==0) &
            (new_df['Need F2F?'] ==0)]
    F2F_eve_df_complete_virtual = new_df[(new_df['Referred_to'] == '121') & 
            (new_df['End'] >= 0) & (new_df['Evening Appt?'] ==1) &
            (new_df['Need F2F?'] ==0)] 
    F2F_eve_df_waiting_virtual = new_df[(new_df['Referred_to'] == '121') & 
            (new_df['End'].isnull().values) & (new_df['Evening Appt?'] ==1) &
            (new_df['Need F2F?'] ==0)] 
    GRP_day_df_complete = new_df[(new_df['Referred_to'] == 'Group') & 
            (new_df['End'] >= 0) & (new_df['Evening Appt?'] ==0)] 
    GRP_day_df_waiting = new_df[(new_df['Referred_to'] == 'Group') & 
            (new_df['End'].isnull().values) & (new_df['Evening Appt?'] ==0)]
    GRP_eve_df_complete = new_df[(new_df['Referred_to'] == 'Group') & 
            (new_df['End'] >= 0) & (new_df['Evening Appt?'] ==1)] 
    GRP_eve_df_waiting = new_df[(new_df['Referred_to'] == 'Group') & 
            (new_df['End'].isnull().values) & (new_df['Evening Appt?'] ==1)]

    def daily_df(df,name, warm_up, sim_duration, second_filter, second_filter_value, third_filter, third_filter_value): 
        if third_filter != '':
            daily_df = df[(df['Referred_to'].isin([name])) & (df[second_filter] == second_filter_value) &
                          (df[third_filter] == third_filter_value)]
        elif second_filter != '':
            daily_df = df[(df['Referred_to'].isin([name])) & (df[second_filter] == second_filter_value)]
        else:
            daily_df = df[(df['Referred_to'].isin([name]))]
        daily_df.drop(columns={'Referred_to','Evening Appt?','Need F2F?','Priority Patient?','Wait time','No of Appts','No: Weeks waiting'}, inplace=True)                         
        daily_df['End'] = daily_df['End'].replace(np.nan,sim_duration+1)#.apply(int)
        for i in range(warm_up, sim_duration):
            a = daily_df[(daily_df['Started Queuing'] <= i) & (daily_df['End'] > i)].count()
            if i == warm_up:
                IESO_summary = (a[0])
            else:
                IESO_summary = np.append(IESO_summary,a[0])
        
        return IESO_summary
    
    IESO_timeline = daily_df(new_df,'IESO',g.warm_up, g.sim_duration,'','','','')
    Group_timeline_day = daily_df(new_df,'Group',g.warm_up, g.sim_duration,'Evening Appt?',0,'','')
    Group_timeline_eve = daily_df(new_df,'Group',g.warm_up, g.sim_duration,'Evening Appt?',1,'','')
    a121_F2F_day_timeline = daily_df(new_df,'121',g.warm_up, g.sim_duration,'Need F2F?',1,'Evening Appt?',0)
    a121_virtual_day_timeline = daily_df(new_df,'121',g.warm_up, g.sim_duration,'Need F2F?',0,'Evening Appt?',0)
    a121_F2F_eve_timeline = daily_df(new_df,'121',g.warm_up, g.sim_duration,'Need F2F?',1,'Evening Appt?',1)
    a121_virtual_eve_timeline = daily_df(new_df,'121',g.warm_up, g.sim_duration,'Need F2F?',0,'Evening Appt?',1)
  
#Streamlit metrics

IESO_s_delta = round(sum(IESO_df_complete['Wait time'])/len(IESO_df_complete['Wait time']),1)
F2F_s_day_delta = round(F2F_day_df_complete['Wait time'].sum()/len(F2F_day_df_complete['Wait time']),1)
F2F_s_eve_delta = round (F2F_eve_df_complete['Wait time'].sum()/len(F2F_eve_df_complete['Wait time']),1)
F2F_s_day_delta_virtual = round(F2F_day_df_complete_virtual['Wait time'].sum()/len(F2F_day_df_complete_virtual['Wait time']),1)
F2F_s_eve_delta_virtual = round (F2F_eve_df_complete_virtual['Wait time'].sum()/len(F2F_eve_df_complete_virtual['Wait time']),1)
GRP_s_day_delta = round(GRP_day_df_complete['Wait time'].sum()/len(GRP_day_df_complete['Wait time']),1)
GRP_s_eve_delta = round(GRP_eve_df_complete['Wait time'].sum()/len(GRP_eve_df_complete['Wait time']),1)


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
tab31, tab32 = st.tabs(["Total Clients Seen", "Total Clients Waiting"])
with tab31:
    #expander('Total Clients Seen'):
    st.subheader('''Total Clients Seen''')
    col16,col17,col18,col19 = st.columns (4)
    
    F2F_Day_s = col16.metric(label = '121 F2F Day patients seen', 
     value = F2F_day_df_complete['End'].count(), 
     delta = f"average wait {F2F_s_day_delta} weeks")
    F2F_Eve_s = col17.metric(label = '121 F2F Eve patients seen', 
     value = F2F_eve_df_complete['End'].count(), 
     delta = f"average wait {F2F_s_eve_delta} weeks")
    F2F_Day_s_virtual = col18.metric(label = '121 Virtual Day patients seen', 
     value = F2F_day_df_complete_virtual['End'].count(), 
     delta = f"average wait {F2F_s_day_delta_virtual} weeks")
    F2F_Eve_s_virtual = col19.metric(label = '121 Virtual Eve patients seen', 
     value = F2F_eve_df_complete_virtual['End'].count(), 
     delta = f"average wait {F2F_s_eve_delta_virtual} weeks")
    
    IESO_s = col16.metric(label = 'IESO patients seen', 
     value = IESO_df_complete['End'].count(), 
     delta = f"average wait {IESO_s_delta} weeks")
    Group_Day_s = col17.metric(label = 'Group Day patients seen', 
     value = GRP_day_df_complete['End'].count(), 
     delta = f"average wait {GRP_s_day_delta} weeks")
    Group_Eve_s =col18.metric(label = 'Group Eve patients seen', 
     value = GRP_eve_df_complete['End'].count(), 
     delta = f"average wait {GRP_s_eve_delta} weeks")

with tab32: 
#st.expander('Number of waiting clients'):
    #st.markdown('##')
    st.subheader('''Number of waiting Clients''')
    col1,col2,col3,col4 = st.columns (4)
    #Priority
    if len(F2F_day_df_waiting) > 0:
        F2F_day_delta = round(F2F_day_df_waiting['No: Weeks waiting'].sum()/len(F2F_day_df_waiting['No: Weeks waiting']),1)
        F2F_day_delta_text = f"average wait {F2F_day_delta} weeks"
    else:
        F2F_day_delta = 'WL Cleared'
        F2F_day_delta_text = 'WL Cleared'
    if len(F2F_eve_df_waiting) > 0:
        F2F_eve_delta =round(F2F_eve_df_waiting['No: Weeks waiting'].sum()/len(F2F_eve_df_waiting['No: Weeks waiting']),1)
        F2F_eve_delta_text = f"average wait {F2F_eve_delta} weeks"
    else:
        F2F_eve_delta = 'WL Cleared'
        F2F_eve_delta_text = 'WL Cleared'
    
    if len(F2F_day_df_waiting_virtual) > 0:
        F2F_day_delta_virtual = round(F2F_day_df_waiting_virtual['No: Weeks waiting'].sum()/len(F2F_day_df_waiting_virtual['No: Weeks waiting']),1)
        F2F_day_delta_text_virtual = f"average wait {F2F_day_delta_virtual} weeks"
    else:
        F2F_day_delta_virtual = 'WL Cleared'
        F2F_day_delta_text_virtual = 'WL Cleared'
    if len(F2F_eve_df_waiting_virtual) > 0:
        F2F_eve_delta_virtual =round(F2F_eve_df_waiting_virtual['No: Weeks waiting'].sum()/len(F2F_eve_df_waiting_virtual['No: Weeks waiting']),1)
        F2F_eve_delta_text_virtual = f"average wait {F2F_eve_delta_virtual} weeks"
    else:
        F2F_eve_delta_virtual = 'WL Cleared'
        F2F_eve_delta_text_virtual = 'WL Cleared'
    
    if len(IESO_df_waiting) > 0:
        IESO_delta = round(IESO_df_waiting['No: Weeks waiting'].sum()/len(IESO_df_waiting['No: Weeks waiting']),1)
        IESO_delta_text = f"average wait {IESO_delta} weeks"
    else:
        IESO_delta = 'WL Cleared'
        IESO_delta_text = 'WL Cleared'
    
    if len(GRP_day_df_waiting) > 0:
        GRP_day_delta = round(GRP_day_df_waiting['No: Weeks waiting'].sum()/len(GRP_day_df_waiting['No: Weeks waiting']),1)
        GRP_day_delta_text = f"average wait {GRP_day_delta} weeks"
    else:
        GRP_day_delta = 'WL Cleared'
        GRP_day_delta_text = 'WL Cleared'
    if len(GRP_eve_df_waiting) > 0:
        GRP_eve_delta = round(GRP_eve_df_waiting['No: Weeks waiting'].sum()/len(GRP_eve_df_waiting['No: Weeks waiting']),1)
        GRP_eve_delta_text = f"average wait {GRP_eve_delta} weeks"
    else:
        GRP_eve_delta = 'WL Cleared'
        GRP_eve_delta_text = 'WL Cleared'
        

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

F2F_Day_w = col1.metric(label = '121 F2F Day patients waiting', 
 value = F2F_day_df_waiting['Need F2F?'].count(), delta = F2F_day_delta_text)
F2F_Eve_w = col2.metric(label = '121 F2F Eve patients waiting', 
 value = F2F_eve_df_waiting['Need F2F?'].count(), delta = F2F_eve_delta_text)
F2F_Day_w_virtual = col3.metric(label = '121 Virtual Day patients waiting', 
 value = F2F_day_df_waiting_virtual['Need F2F?'].count(), delta = F2F_day_delta_text_virtual)
F2F_Eve_w_virtual = col4.metric(label = '121 Virtual Eve patients waiting', 
 value = F2F_eve_df_waiting_virtual['Need F2F?'].count(), delta = F2F_eve_delta_text_virtual)

IESO_w = col1.metric(label = 'IESO patients waiting', 
 value = IESO_df_waiting['Need F2F?'].count(), delta = IESO_delta_text)
Group_Day_w = col2.metric(label = 'Group Day patients waiting', 
 value = GRP_day_df_waiting['Need F2F?'].count(), delta = GRP_day_delta_text)
Group_Eve_w =col3.metric(label = 'Group Eve patients waiting', 
 value = GRP_eve_df_waiting['Need F2F?'].count(), delta = GRP_eve_delta_text)

st.markdown('##')
st.write('''Priority and no priority current assessed as one group''')

st.markdown('##')
#with st.expander('Data Tables'):
st.subheader('Data Tables')
st.write('Table of waiting referrals')
tab11, tab12, tab13, tab14, tab15, tab16, tab17 = st.tabs(["🗃 IESO", "🗃 121 F2F Day",'🗃 121 Virtual Day','🗃 121 F2F Eve','🗃 121 Virtual Eve', '🗃 Group Day','🗃 Group Eve'])

st.write('Table of complete referrals')
tab21, tab22, tab23, tab24, tab25, tab26, tab27 = st.tabs(["🗃 IESO", "🗃 121 F2F Day",'🗃 121 Virtual Day','🗃 121 F2F Eve','🗃 121 Virtual Eve', '🗃 Group Day','🗃 Group Eve'])

tab21.write('IESO complete')
tab21.dataframe(IESO_df_complete)
tab11.write('IESO waiting')
tab11.dataframe(IESO_df_waiting)
tab22.write('121 Face to face day complete') 
tab22.dataframe(F2F_day_df_complete)
tab12.write('121 Face to face day waiting')
tab12.dataframe(F2F_day_df_waiting)
tab23.write('121 Virtual day complete') 
tab23.dataframe(F2F_day_df_complete_virtual)
tab13.write('121 Virtual day waiting')
tab13.dataframe(F2F_day_df_waiting_virtual)
tab24.write('121 Face to face evening complete')
tab24.dataframe(F2F_eve_df_complete)
tab14.write('121 Face to face evening waiting')
tab14.dataframe(F2F_eve_df_waiting)
tab25.write('121 Virtual evening complete') 
tab25.dataframe(F2F_eve_df_complete_virtual)
tab15.write('121 Virtual eve waiting')
tab15.dataframe(F2F_eve_df_waiting_virtual)
tab26.write('Group day complete')
tab26.dataframe(GRP_day_df_complete)
tab16.write('Group day waiting')
tab16.dataframe(GRP_day_df_waiting)
tab27.write('Group evening complete')
tab27.dataframe(GRP_eve_df_complete)
tab17.write('Group evening waiting')
tab17.dataframe(GRP_eve_df_waiting)
    