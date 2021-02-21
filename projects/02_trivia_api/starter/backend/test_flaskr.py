import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres:///{}".format(self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'answer':'Orchids',
            'question':'Which flower family produces vanilla?',
            'category':'1',
            'difficulty': 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        print('***Test Setup Completed***')
    
    def tearDown(self):
        """Executed after reach test"""
        print('***Test TearDown Completed***')
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        res = self.client().get('/questions')
        print('debugging valid questions request: '+str(res))
        #print(res.data)
        data = json.loads(res.data.decode('utf-8'))
        #print(data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_questions_beyond_range_404(self):
        res = self.client().get('/questions?page=300000')
        print('debugging invalid question range: '+str(res))
        data=json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found. Sorry!')

    def test_get_categories(self):
        res = self.client().get('/categories')
        print('debugging valid category request: '+str(res))
        #print(res.data)
        data = json.loads(res.data.decode('utf-8'))
        #print(data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(data['categories'])

    def test_category_error_404(self):
        res = self.client().get('/categories/1')
        print('debugging invalid category request: '+str(res))
        data=json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found. Sorry!')


    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions')
        print('debugging successful category question request: '+str(res))
        data=json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_categories'])

    def test_invalid_category_questions_404(self):
        res = self.client().get('/categories/30000/questiones')
        print('debugging invalid category question request: '+str(res))
        data=json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Resource Not Found. Sorry!')
    
    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        print('debugging successful create question: '+str(res))
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # def test_create_question_empty_500(self):
    #     res = self.client().post('/questions')
    #     print('debugging create question empty: '+str(res))
    #     data = json.loads(res.data.decode('utf-8'))
    #     self.assertEqual(res.status_code, 500)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'There was a problem with the server. Please try again later.')
    

    def test_create_question_not_allowed_405(self):
        res = self.client().post('/questions/1', json=self.new_question)
        print('debugging create question fail: '+str(res))
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'That method is not allowed for this endpoint.')

    def test_delete_question(self):
        res = self.client().delete('/questions/4')
        print('debugging normal delete: '+str(res))
        data = json.loads(res.data.decode('utf-8'))
        question=Question.query.filter(Question.id==4).one_or_none()
        print(question)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_delete_nonexistent_question_422(self):
        res = self.client().delete('/questions/34567')
        print('debugging delete nonexistent: '+str(res))
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable. This request was formatted well, but may have semantic errors.')

    def test_successful_search(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'lake'})
        print('debugging test_successful_search: '+str(res))
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 1)

    def test_empty_search(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'unicorns'})
        print('debugging test_empty_search: '+str(res))
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], [])
        self.assertEqual(len(data['questions']), 0)

    def test_quiz(self):
        res = self.client().post('/quizzes', json={
    "finished_questions":[],
    "quiz_category":{"id":0}
})
        print('debugging test_quiz: '+str(res))
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
    
    def test_nonexistent_quiz_422(self):
        res = self.client().post('/quizzes', json={
    "finished_questions":[],
    "quiz_category":{"id":26000}
})
        print('debugging test_nonexistent_quiz: '+str(res))
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable. This request was formatted well, but may have semantic errors.')

    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()