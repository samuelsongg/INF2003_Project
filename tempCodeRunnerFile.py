@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        productName = request.form['productName']
        productStock = request.form['productStock']
        productCategory = request.form['productCategory']
        productPrice = request.form['productPrice']
        productDescription = request.form['productDescription']

        db.products.insert_one({
            "name": productName,
            "stock": productStock,
            "category": productCategory,
            "price": productPrice,
            "description": productDescription
        })
        
        flash("Added new item successfully", "success")
        return redirect("/add_item")
    
    return render_template('add_item.html')