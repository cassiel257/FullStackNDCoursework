import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE, OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories=Category.query.all()
    trial={c.id:c.type for c in Category.query.all()}
    if len(trial) == 0:
      abort(404)
    else:
      return jsonify({"success": True, "categories":trial, "total_categories":len(trial)})

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    selection=Question.query.all()
    current_questions=paginate_questions(request, selection)
    cats={c.id:c.type for c in Category.query.all()}

    if len(current_questions) == 0:
      abort(404)
    else:  
      return jsonify({"success": True, "questions":current_questions, "total_questions":len(Question.query.all()), "categories":cats, 'current_category':None})
    
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      if not question:
        abort(404)
      else:
        question.delete()
        selection=Question.query.all()
        current_questions=paginate_questions(request, selection)
        return jsonify({"success": True, "questions":current_questions, "total questions":len(Question.query.all())})

    except Exception as e:
      print(e)
      abort(422)
  
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    answer=body.get('answer', None)
    question=body.get('question', None)
    category=body.get('category', None)
    difficulty=body.get('difficulty', None)

    try:
      if question is None:
        abort(422)
      else:
        question=Question(answer=answer, question=question, category=category, difficulty=difficulty)
        question.insert()
        selection=Question.query.all()
        current_questions=paginate_questions(request, selection)
        return jsonify({'success':True, 'created': question.id, 'questions':current_questions, 'total_questions':len(Question.query.all())})
    except Exception as e:
      #print("Exception is ", e)
      abort(500)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search():
    body=request.get_json()
    searchTerm=body.get('searchTerm','')
    try:
      results = Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
      filtered_questions= paginate_questions(request, results)
      return jsonify({ 'success':True, 'questions':filtered_questions, 'total_questions':len(Question.query.all()), 'current_category':None})
    
    except Exception as e:
      print("Exception is ", e)
      abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def category_questions(category_id):
    body=request.get_json()
    try:
      questions=Question.query.filter(Question.category==str(category_id)).all()
      filtered_questions=paginate_questions(request, questions)
      return jsonify({'success':True, 'questions':filtered_questions, 'total_categories':len(Category.query.all())})

    except Exception as e:
      print("Exception is ", e)
      abort(400)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  
  @app.route('/quizzes', methods=['POST'])
  def play_trivia():
    body = request.get_json()

    finished_questions = body.get("finished_questions", [])
    quiz_category = body.get("quiz_category", None)

    try:
      quiz=[]
      if quiz_category:
        if quiz_category["id"] == 0:
        #if quiz_category["type"] == "click":
          quiz = [ques for ques in Question.query.all()]

        else:
          quiz = [ques for ques in Question.query.filter_by(category=quiz_category["id"]).all()]

        if not quiz:
          return abort(422)
        print("Here is your list of questions: "+str(quiz))  

      bank = []

      for qz in quiz:
        if qz.id not in finished_questions:
          bank.append(qz.format())

      if len(bank) != 0:
        result = random.choice(bank)
        return jsonify({"success": True, "question": result})

      else:
        return jsonify({"question": False, "message":"No questions remaining."})

    except Exception as e:
      print('The error is >> ',e)
      abort(422)
  # @app.route('/play', methods=['POST'])
  # def play_function():
  #   body=request.get_json()
  #   quiz_category=body.get('quiz_category', None)
  #   finished_quiz=body.get('finished_quiz', [])
  #   quiz=[]
  #   section=[]
  #   try:
  #     if quiz_category:
  #       quiz_category='quiz_category'
  #       if quiz_category['id']==0:
  #         quiz=Question.query.all()
  #       else:
  #         quiz=Question.query.filter_by(category=quiz_category['id']).all()

  #     if quiz:
  #       for q in quiz:
  #         if question.id not in finished_quiz:
  #           section.append(question.format())
  #     else:
  #       return abort(422)
  #     if len(section)!=0:
  #       result=random.choice(section)
  #       return jsonify({"success":True, "question":result})
  #     else:
  #       return jsonify({"success":False, "question":False})
  #   except Exception as e:
  #     print("Exception is ", e)
  #     abort(422)

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request. Please check your data and try again."
      }), 400
    
  @app.errorhandler(404)
  def not_found(error):
     return jsonify({
         "success": False,
         "error": 404,
         "message": "Resource Not Found. Sorry!"
     }), 404

  @app.errorhandler(405)
  def not_allowed(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "That method is not allowed for this endpoint."
      }), 405
    
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable. This request was formatted well, but may have semantic errors."
      }), 422

  @app.errorhandler(500)
  def server_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "There was a problem with the server. Please try again later."
      }), 500

  return app

    