from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Reflection, Comment
from app.classes.forms import ReflectionForm, CommentForm
from flask_login import login_required
import datetime as dt


@app.route('/reflection/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def reflectionNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = ReflectionForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new blog form. 
        # Blog() is a mongoengine method for creating a new blog. 'newBlog' is the variable 
        # that stores the object that is the result of the Blog() method.  
        newReflection = Reflection(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            memory = form.memory.data,
            happiness = form.happiness.data,
            symbol = form.symbol.data,
            author = current_user.id,
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newReflection.save()

        # Once the new blog is saved, this sends the user to that blog using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a blog so we want 
        # to send them to that blog. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('reflection',reflectionID=newReflection.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at blogform.html to 
    # see how that works.
    return render_template('reflectionform.html',form=form)

@app.route('/reflection/<reflectionID>')
# This route will only run if the user is logged in.
@login_required
def reflection(reflectionID):
    
    thisReflection = Reflection.objects.get(id=reflectionID)
 
    theseComments = Comment.objects(reflection=thisReflection)

    return render_template('reflection.html',reflection=thisReflection,comments=theseComments)





@app.route('/reflections')
@login_required

def reflections():
    reflections = Reflection.objects()
    return render_template("reflections.html",reflections=reflections)

@app.route('/reflection/delete/<reflectionId>')
@login_required

def reflectionDelete(reflectionId):
    delReflection = Reflection.objects.get(id=reflectionId)
    sleepDate = delReflection.reflection_date
    delReflection.delete()
    flash(f"reflection with date {reflectionDate} has been deleted.")
    return redirect(url_for('reflections'))

@app.route('/reflection/edit/<reflectionID>', methods=['GET', 'POST'])
@login_required
def reflectionEdit(reflectionID):
    editReflection = Reflection.objects.get(id=reflectionID)
    # if the user that requested to edit this blog is not the author then deny them and
    # send them back to the blog. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editReflection.author:
        flash("You can't edit a blog you don't own.")
        return redirect(url_for('reflection',reflectionID=reflectionID))
    # get the form object
    form = ReflectionForm()
    # If the user has submitted the form then update the blog.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editReflection.update(
            memory = form.memory.data,
            happiness = form.happiness.data,
            symbol = form.symbol.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated blog using a redirect.
        return redirect(url_for('reflection',reflectionID=reflectionID))
    
     # if the form has NOT been submitted then take the data from the editBlog object
    # and place it in the form object so it will be displayed to the user on the template.
    form.memory.data = editReflection.memory
    form.happiness.data = editReflection.happiness
    form.symbol.data = editReflection.symbol


    # Send the user to the blog form that is now filled out with the current information
    # from the form.
    return render_template('reflectionform.html',form=form)
