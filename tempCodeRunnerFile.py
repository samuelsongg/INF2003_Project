@app.route('/detailedItem/<product_id>', methods=['GET', 'POST'])
def detailedItem(product_id):
    if request.method == 'GET':
        product_id = ObjectId(product_id)
        product = db.product.find_one({"_id": product_id})
        return render_template('detailedItem.html', product_id=str(product_id), product=product)
    
    if request.method == 'POST':
        if 'selectedRating' in request.form:
            reviewTitle = request.form['reviewTitle']
            reviewDescription = request.form['reviewDescription']
            reviewRating = request.form['reviewRating']
            user_id = session['user_id']

            try:
                conn = get_db_connection()
                conn.execute('INSERT INTO review (user_id, review_title, review_description, review_rating, product_id) VALUES (?, ?, ?, ?, ?)', (user_id, reviewTitle, reviewDescription, reviewRating, product_id))
                conn.commit()
                conn.close()
                return redirect(url_for('detailedItem', product_id=product_id))
            
            except Exception as e:
                print(str(e))
                return render_template('index.html')
            
    return redirect(url_for('detailedItem', product_id=product_id)) 