from ayten_gradproj import preprocess_text, calculate_tfidf, get_recommendations,pdf2text,os,preprocessing
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import logging
#delete last row
# CSV_FILE = '/Users/Ayten/Desktop/gradcode/last_3_columns_tfidf.csv'
# x = pd.read_csv(CSV_FILE)
# # Drop the last row
# x = x[:-1]
# # Save the DataFrame back to the CSV file
# x.to_csv(CSV_FILE, index=False)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

import os
if not os.path.isdir(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html', error_message=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error_message="No file part")
    
    file = request.files['file']
    
    if file.filename == '':
        return render_template('index.html', error_message="No selected file")
    
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # name = file.filename
        
        
        file.save(file_path)
        
        # Assuming pdf2text returns a string
        extracted_text = pdf2text(file_path)
        # extracted_text = "When you delete a file or a folder, OneDrive gives you a chance to undo your decision but even if you miss the opportunity, you can s;ll get the file back. In the naviga;on pane, click Recycle bin. As you can see OneDrive doesn't really delete items and moves them here so you can get"
       
        CSV_FILE = '/Users/Ayten/Desktop/gradcode/last_3_columns_tfidf.csv'

       # Load the existing CSV if it exists, otherwise create an empty DataFrame
        
        csv_df = pd.read_csv(CSV_FILE)
        preprocessed_text = preprocess_text(extracted_text, file.filename)
        # Append the preprocessed text to the DataFrame
        # csv_df = csv_df.append(preprocessed_text, ignore_index=True)
        csv_df = pd.concat([csv_df, preprocessed_text], ignore_index=True)
        csv_df.tail(3)
        print("last three rows: ",csv_df.tail(3) )
        
        # Save the updated DataFrame back to the CSV file
        # csv_df.to_csv(CSV_FILE, index=False)

        # preprocessed_text.to_csv(csv_df, mode='a', header=not os.path.exists(csv_df), index=False)
        
        tfidf_result = calculate_tfidf(csv_df)
        print("index colomn DOCUMENT: ", tfidf_result.columns)
        recommendations = get_recommendations(file.filename,tfidf_result)
        print("top recommendations debugging:",recommendations)
        print("type reccommendation before conversion: ",type(recommendations))
        # Check if recommendations is a valid object for render_template
        if isinstance(recommendations, pd.Series):
            recommendations = recommendations.tolist()
        # recommendations = get_recommendations('Recycle bin',tfidf_result)
        # Remove the uploaded file after processing
        print("type reccommendation after conversion: ",type(recommendations))
        print("filename uploaded:",file.filename)

        recommendations_names, recommendations_descriptions = get_recommendations(file.filename, tfidf_result)


        os.remove(file_path)
        
        #  # Prepare enumerated list for template rendering
        enumerated_recommendations = list(enumerate(zip(recommendations_names, recommendations_descriptions), 1))
        print("enumerated recommendations zipped together:",enumerated_recommendations )

        enumerated_recommendations = list(enumerate(zip(recommendations_names, recommendations_descriptions), 1))
        return render_template('display_text.html', enumerated_recommendations=enumerated_recommendations)
        # return render_template('display_text.html', recommendations=recommendations)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
