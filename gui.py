import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import webbrowser
import re

class FarcasterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Farcaster User Insights")
        self.geometry("1280x720")
        self.dataframe = self.load_and_prepare_data()
        self.create_widgets()

    def load_and_prepare_data(self):
        user_data = pd.read_csv('aggregated_token_balances_v2.csv')
        link_data = pd.read_csv('All_Active_Farcaster_Users.csv')
        link_data['fname_link'] = link_data['fname_link'].apply(self.extract_url)
        combined_data = pd.merge(user_data, link_data[['fname', 'fname_link']], on='fname', how='left')
        return combined_data

    def extract_url(self, html_link):
        if pd.isna(html_link):
            return None
        match = re.search(r'href=[\'"]?([^\'" >]+)', html_link)
        return match.group(1) if match else None

    def create_widgets(self):
        self.configure(bg='#f0f0f0')
        search_frame = tk.Frame(self, bg='#f0f0f0')
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        self.entry = ttk.Entry(search_frame, font=('Arial', 12))
        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(search_frame, text="Search", command=self.load_user_data).pack(side=tk.LEFT, padx=10)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.user_frame = ttk.Frame(self.notebook)
        self.popularity_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.user_frame, text="User Data")
        self.notebook.add(self.popularity_frame, text="Token Popularity")

        self.left_frame = tk.Frame(self.user_frame, width=640, bg='#f0f0f0')
        self.right_frame = tk.Frame(self.user_frame, width=640, bg='#f0f0f0')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_user_data(self):
        username = self.entry.get().strip()
        user_data = self.dataframe[self.dataframe['fname'] == username]
        if user_data.empty:
            messagebox.showerror("Error", "User not found. Please enter a valid username.")
            return
        user_data = user_data.iloc[0]
        self.display_user_data(user_data)
        self.find_similar_users(username)
        self.display_token_popularity()

    def display_user_data(self, user_data):
        for widget in self.left_frame.winfo_children() + self.right_frame.winfo_children():
            widget.destroy()
        
        if pd.notna(user_data['fname_link']):
            profile_button = tk.Button(self.left_frame, text=f"Visit {user_data['fname']}'s Profile", 
                                       command=lambda: webbrowser.open_new(user_data['fname_link']),
                                       bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
            profile_button.pack(pady=10)
        
        portfolio_text = tk.Text(self.left_frame, wrap=tk.WORD, height=15, width=50, font=('Arial', 10), bg='white')
        portfolio_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        portfolio_text.tag_configure("link", foreground="blue", underline=1)
        portfolio_text.tag_configure("bold", font=('Arial', 10, 'bold'))
        portfolio_text.insert(tk.END, "Token\tValue\n", "bold")
        
        for i in range(1, 11):
            token = user_data[f'token_{i}_symbol']
            value = user_data[f'token_{i}_usd_value']
            address = user_data[f'token_{i}_address']
            if pd.notna(token) and pd.notna(value):
                portfolio_text.insert(tk.END, f"{token}\t", "link")
                portfolio_text.insert(tk.END, f"${value:.2f}\n")
                portfolio_text.tag_bind(f"link_{i}", "<Button-1>", lambda e, addr=address: self.open_token_link(addr))
                portfolio_text.tag_add(f"link_{i}", f"{i+1}.0", f"{i+1}.{len(token)}")
        
        portfolio_text.config(state=tk.DISABLED)
        
        self.create_pie_chart(self.right_frame, user_data)

    def find_similar_users(self, username):
        target_user_tokens = set(self.dataframe[self.dataframe['fname'] == username]
                                 [[f'token_{i}_symbol' for i in range(1, 11)]].values[0])
        target_user_tokens = {token for token in target_user_tokens if pd.notna(token)}

        similarities = []
        for _, row in self.dataframe.iterrows():
            if row['fname'] != username:
                user_tokens = set(row[[f'token_{i}_symbol' for i in range(1, 11)]])
                user_tokens = {token for token in user_tokens if pd.notna(token)}
                
                intersection = len(target_user_tokens.intersection(user_tokens))
                union = len(target_user_tokens.union(user_tokens))
                jaccard_similarity = intersection / union if union > 0 else 0
                
                similarities.append((row['fname'], jaccard_similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        similar_users = similarities[:3]

        tk.Label(self.left_frame, text="Similar Users", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(fill=tk.X, pady=(20, 5))
        
        similar_users_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        similar_users_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(similar_users_frame, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(similar_users_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for similar_user, similarity in similar_users:
            user_info = self.dataframe[self.dataframe['fname'] == similar_user].iloc[0]
            frame = tk.Frame(scrollable_frame, bg='white', bd=1, relief=tk.SOLID)
            frame.pack(fill=tk.X, pady=5)
            label = tk.Label(frame, text=f"{user_info['fname']} (Similarity: {similarity:.2f})", font=('Arial', 10, 'bold'), bg='white')
            label.pack(fill=tk.X, padx=5, pady=2)
            if pd.notna(user_info['fname_link']):
                link_label = tk.Label(frame, text="Visit Profile", cursor="hand2", fg="blue", bg='white', font=('Arial', 8))
                link_label.pack(padx=5, pady=2)
                link_label.bind("<1>", lambda e, link=user_info['fname_link']: webbrowser.open_new(link))
            
            portfolio_text = tk.Text(frame, wrap=tk.WORD, height=5, width=50, font=('Arial', 8), bg='white')
            portfolio_text.pack(fill=tk.X, expand=False, padx=5, pady=2)
            portfolio_text.tag_configure("link", foreground="blue", underline=1)
            portfolio_text.insert(tk.END, "Token\tValue\n", "bold")
            
            for i in range(1, 11):
                token = user_info[f'token_{i}_symbol']
                value = user_info[f'token_{i}_usd_value']
                address = user_info[f'token_{i}_address']
                if pd.notna(token) and pd.notna(value):
                    portfolio_text.insert(tk.END, f"{token}\t", "link")
                    portfolio_text.insert(tk.END, f"${value:.2f}\n")
                    portfolio_text.tag_bind(f"link_{i}", "<Button-1>", lambda e, addr=address: self.open_token_link(addr))
                    portfolio_text.tag_add(f"link_{i}", f"{i+1}.0", f"{i+1}.{len(token)}")
            
            portfolio_text.config(state=tk.DISABLED)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_pie_chart(self, frame, user_data):
        fig, ax = plt.subplots(figsize=(8, 8))
        token_values = {user_data[f'token_{i}_symbol']: user_data[f'token_{i}_usd_value'] for i in range(1, 11) if user_data[f'token_{i}_usd_value'] > 0}
        labels = [f"{token}" for token in token_values.keys()]
        sizes = list(token_values.values())
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, pctdistance=0.85)
        
        plt.setp(autotexts, size=8, weight="bold", color="black")
        plt.setp(texts, size=0)  # Hide the default labels
        
        ax.set_title(f"Portfolio of {user_data['fname']}", fontsize=16, pad=20)
        
        ax.legend(wedges, labels,
                  title="Tokens",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        
        chart = FigureCanvasTkAgg(fig, frame)
        chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def open_token_link(self, address):
        if pd.notna(address):
            url = f"https://dexscreener.com/base/{address}"
            webbrowser.open_new(url)
        else:
            messagebox.showinfo("Info", "Token address not available.")

    def display_token_popularity(self):
        popularity_df = self.aggregate_token_popularity()
        ranked_tokens = self.rank_tokens(popularity_df)
        
        for widget in self.popularity_frame.winfo_children():
            widget.destroy()
        
        label = tk.Label(self.popularity_frame, text="Top 50 Most Popular Tokens", font=('Arial', 14, 'bold'))
        label.pack(pady=10)
        
        tree = ttk.Treeview(self.popularity_frame, columns=('Token', 'Holders', 'Total Value'), show='headings')
        tree.heading('Token', text='Token')
        tree.heading('Holders', text='Holders')
        tree.heading('Total Value', text='Total Value')
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for index, row in ranked_tokens.iterrows():
            tree.insert('', 'end', values=(index, row['holders'], f"${row['total_value']:,.2f}"))

    def aggregate_token_popularity(self):
        token_popularity = {}
        for i in range(1, 11):
            symbol_col = f'token_{i}_symbol'
            value_col = f'token_{i}_usd_value'
            for index, row in self.dataframe.iterrows():
                symbol = row[symbol_col]
                value = row[value_col]
                if pd.notna(symbol) and pd.notna(value):
                    if symbol in token_popularity:
                        token_popularity[symbol]['total_value'] += value
                        token_popularity[symbol]['holders'] += 1
                    else:
                        token_popularity[symbol] = {'total_value': value, 'holders': 1}
        
        popularity_df = pd.DataFrame.from_dict(token_popularity, orient='index')
        popularity_df.columns = ['total_value', 'holders']
        return popularity_df

    def rank_tokens(self, popularity_df):
        popularity_df.sort_values(by=['holders', 'total_value'], ascending=[False, False], inplace=True)
        return popularity_df.head(50)

if __name__ == "__main__":
    app = FarcasterApp()
    app.mainloop()