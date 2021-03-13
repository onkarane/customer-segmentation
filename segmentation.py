#import required libraries
import pandas as pd

class Transformation:

    '''
    Class provides functionality to perform
    data wrangling operations on the starbucks data.
    '''

    def get_offer_time(df):
        '''
        Function computes time for when the customer
        received/viewed/completed each of the unique offer.

        INPUT:
            1. df(pandas dataframe): dataframe with one-hot encoded
                                    values for each of the three events
        
        OUTPUT: 
            1. final_df(pandas dataframe): dataframe with the offer
                                            received/viewed/completed time
                                            for each user.
        '''
        #multiply time with each of the one-hot encoded variable
        df['completed_time'] = df['offer_completed'] * df['time']
        df['received_time'] = df['offer_received'] * df['time']
        df['viewed_time'] = df['offer_viewed'] * df['time']

        #process the new dimensions for each person and offer
        processed_time_dim = df.groupby(by=['person', 'new_offer_ids', 'time']) \
                                .max().unstack()
        processed_time_dim.fillna(0, inplace=True)

        #dataframe to return
        final_df = pd.DataFrame(
                        processed_time_dim.index.get_level_values('new_offer_ids'),
                        processed_time_dim.index.get_level_values('person')) \
                        .reset_index()
        #assign processed values to new columns in the final dataframe
        final_df['received_time'] = processed_time_dim['received_time'].values.max(axis=1)
        final_df['viewed_time'] = processed_time_dim['viewed_time'].values.max(axis=1)
        final_df['completed_time'] = processed_time_dim['completed_time'].values.max(axis=1)

        return final_df

    def get_valid_offers(df):
        '''
        Function filters out the invalid offers based on the criteria offer 
        received/viewed/completed should be less than end time. The function also 
        adds two new columns that represent whether the offer was viewed & completed 
        on time.

        INPUT: 
            1. df(pandas dataframe): dataframe with received/viewed/completed
                                    time for each offer as well the offer end time.
            
        OUTPUT:
            1. valid_offers(pandas dataframe): dataframe with only the valid transactions.
        '''
        
        #drop the invalid offers
        valid_offers = df.query('~(completed_time > 0 and viewed_time == 0)') # completed without viewing
        valid_offers = valid_offers.query('~(completed_time != 0 and completed_time < viewed_time)') #completed before viewing
        valid_offers = valid_offers.query('~(viewed_time != 0 and viewed_time < received_time)')#viewed before receving

        return valid_offers

    def __process_offers(df, col,opr_type):
        '''
        A private function to calculate view rate and completed rate for each general offer
        Ex offer: bogo or informational. This function will be called by the get_offer_rates.

        INPUT:
            1. df(pandas dataframe): dataframe with values pertaining to indvidual offer
            2. col('string'): name of the individual offer
            3. opr_type(string): name of the operation to perform i.e calculcate view rate or completion rate
                                values: completed or viewed
        
        OUTPUT:
            1. rate_df(pandas dataframe): a grouped dataframe with person id as the index
        '''
        if opr_type == "viewed":
            colname = col + "_vr"
            total_viewed = pd.DataFrame(df.query('viewed_time != 0') \
                            .groupby('person')['new_offer_ids'].count())
        else:
            colname = col + "_cr"
            total_viewed = pd.DataFrame(df.query('completed_time != 0') \
                                .groupby('person')['new_offer_ids'].count())
        #calculate the total
        total_received = pd.DataFrame(df.groupby('person')['new_offer_ids'].count())
        #calculate view rate
        rate_df = pd.DataFrame(round(total_viewed['new_offer_ids'] / total_received['new_offer_ids'],2)) \
                    .rename(columns = {"new_offer_ids" : colname})
            
        return rate_df.rename_axis("person")
    
    def get_offer_rates(df, cust):
        '''
        A public function that will call the respective private function to calculate 
        the values for individual offers and append them as new columns to the cust dataframe.

        INPUT:
            1. df(pandas dataframe): dataframe with all the values to calculcate offer rates
            2. cust(pandas dataframe): a dataframe with person id as the index
        
        OUTPUT:
            1. cust (pandas dataframe):  dataframe with values of rates appended as columns to it
        '''
        #loop thru and get rates for individual offers
        for o in df['offer_type'].unique().tolist():
            filtered_data = df[df['offer_type'] == o]
            gvr_data = Transformation.__process_offers(filtered_data, o, "viewed")
            cust = cust.join(gvr_data)
            cvr_data = Transformation.__process_offers(filtered_data, o, "completed")
            cust = cust.join(cvr_data)
        #fill in the null values with 0
        cust.fillna(0, inplace = True)

        return cust

    def __process_offer_count(df, offer):
        '''
        Private function to calculate the count of 
        offer recevied/viewed/completed
        
        INPUT:
            1. df(pandas dataframe): dataframe to calculate the counts from
            2. offer(string): the name of the offer to calculate the counts for
            
        OUTPUT:
            1.grouped_list: list of grouped data with counts for all three events
        '''
        #list of events
        events = ['received_time', 'viewed_time', 'completed_time']
        grouped_list = []
        
        #loop through the events
        for e in events:
            colname = offer +"_"+ e.split("_")[0] + "_cnt"
            grouped_data = df.query("{} != 0".format(e)) \
                                .groupby("person") \
                                .agg(colname = ("new_offer_ids", "count"))
            #rename the column
            grouped_data = grouped_data.rename(columns = {"colname": colname})
            #append to the list
            grouped_list.append(grouped_data)
            
        return grouped_list

    def get_offer_counts(df, cust):
        '''
        Function to calculate the count of 
        all offer recevied/viewed/completed

        INPUT:
            1. df(pandas dataframe): dataframe with all the values to calculcate offer rates
            2. cust(pandas dataframe): a dataframe with person id as the index
        
        OUTPUT:
            cust(pandas dataframe): dataframe with counts of each offer and associated event
                                    appended to it as columns
        '''
        offer = ['bogo', 'discount', 'informational']
        #loop through the offers
        for o in offer:
            filtered_data = df[df['offer_type'] == o]
            event_list = Transformation.__process_offer_count(filtered_data, o)
            #join the values from the list
            for e in event_list:
                cust = cust.join(e)

        #drop the columns
        cust.drop("informational_completed_cnt", inplace = True, axis = 1)
        #fill nans
        cust.fillna(0, inplace = True)
        
        return cust

    def process_transaction_data(df, cust):
        '''
        Function calculates the total amount spent, total amount rewarded &
        total transactions by each customer.

        INPUT:
            1. df(pandas dataframe): dataframe to calculate the stats from
            2. cust(pandas dataframe): dataframe with person as the index
        
        OUTPUT:
            1. cust(pandas dataframe): dataframe with total amount spent,
                                        total amount rewarded & total transactions
                                        columns appened to it

        '''
        #calculate the total amount spent by the customer
        grouped_amt = df.groupby("person").agg(total_amount = ('amount', 'sum'))
        #calculate the total rewards received by customer
        grouped_rewards = df.groupby("person").agg(total_rewards = ('rewards', 'sum'))
        #calculate total transactions by customer
        df_transaction = df[df['event'] == 'transaction']
        grouped_transactions = df_transaction.groupby("person").agg(total_transactions = ('event', 'count'))
        
        #join to the customer dataframe
        cust = cust.join(grouped_amt)
        cust = cust.join(grouped_rewards)
        cust = cust.join(grouped_transactions)
        
        #fill na
        cust.fillna(0, inplace = True)
        
        return cust

    def process_rewards(df, cust):
        '''
        Function calculates the total amount spent, total amount rewarded &
        total transactions by each customer.

        INPUT:
            1. df(pandas dataframe): dataframe to calculate the stats from
            2. cust(pandas dataframe): dataframe with person as the index
        
        OUTPUT:
            1. cust(pandas dataframe): dataframe with bogo & discount rewards
                                        appended to it

        '''
        #get the bogo rewards
        bogo = df[df['offer_type'] == "bogo"]
        grouped_bogo = bogo.groupby("person").agg(bogo_rewards = ('rewards', 'sum'))
        #get the discount rewards
        discount = df[df['offer_type'] == "discount"]
        grouped_discount = discount.groupby("person").agg(discount_rewards = ('rewards', 'sum'))
        
        #join with cust
        cust = cust.join(grouped_bogo)
        cust = cust.join(grouped_discount)
        
        #fill na
        cust.fillna(0, inplace = True)

        return cust

    def process_event_averages(df, cust):
        '''
        Function calculates the total amount spent, total amount rewarded &
        total transactions by each customer.

        INPUT:
            1. df(pandas dataframe): dataframe to calculate the stats from
            2. cust(pandas dataframe): dataframe with person as the index
        
        OUTPUT:
            1. cust(pandas dataframe): dataframe with avg bogo & discount rewards
                                        appended to it
        '''
        #calculate average amount
        cust['avg_amount'] = round(cust['total_amount'] / cust['total_transactions'])
        #calculate average rewards
        cust['avg_rewards'] = round(cust['total_rewards'] / cust['total_transactions'])

        #get the bogo rewards
        bogo = df[df['offer_type'] == "bogo"]
        grouped_bogo_avg = bogo.groupby("person").agg(avg_bogo_rewards = ('rewards', 'mean'))
        #get the discount rewards
        discount = df[df['offer_type'] == "discount"]
        grouped_discount_avg = discount.groupby("person").agg(avg_discount_rewards = ('rewards', 'mean'))

        #join with the cust
        cust = cust.join(grouped_bogo_avg)
        cust = cust.join(grouped_discount_avg)

        #fill na
        cust.fillna(0, inplace = True)

        return cust

    def one_hot_encode(df):
        '''
        Function one-hot encodes the year and gender column.

        INPUT:
            1. df(pandas dataframe): dataframe to get the gender and year columns from
        
        OUTPUT:
            1. df(pandas dataframe): dataframe with gender & year values one-hot encoded &
                                        appended to it
        '''
        #encode gender
        df = pd.get_dummies(df, columns=['gender'])
        
        #extract the year values
        df['year'] = df.became_member_on.dt.year
        #drop the became_member_on columns
        df.drop('became_member_on', inplace = True, axis = 1)
        #get the dummy variables
        df = pd.get_dummies(df, columns=['year'])

        return df

        