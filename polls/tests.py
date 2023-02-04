import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from polls.models import Choice, Question


def create_question(question_text: str, days: int):
    question = Question.objects.create(
        question_text=question_text, 
        pub_date=timezone.now() + datetime.timedelta(days=days))
    return question


def create_choice(choice_text: str, question: Question):
    choice = Choice.objects.create(choice_text=choice_text, question=question)
    return choice


def get_choice(choice_id: int):
    choice = Choice.objects.get(pk=choice_id)
    return choice


class QuestionModelTest(TestCase):
    def test_get_absolute_url(self):
        """
        Question absolute url should be equal to its detail url
        """
        question = create_question("Question", -12)
        question = Question.objects.get(id=question.id)
        self.assertEqual(question.get_absolute_url(), '/1/')

    def test_str_property_equal_to_question_text(self):
        """
        Question model str method returns its question_text
        """
        question = create_question("Question", -12)
        question = Question.objects.get(id=question.id)
        self.assertEqual(str(question), question.question_text)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['questions'], [])

    def test_get_questions(self):
        """
        Get questions ordered by publish date
        """
        question1 = create_question("Question 1", -12)
        question2 = create_question("Question 2", -10)
        question3 = create_question("Question 3", -7)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['questions'], [question3, question2, question1])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['questions'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['questions'],
            [question],
        )
        

class QuestionDetailViewTests(TestCase):
    def test_question_with_non_existing_id(self):
        """
        The detail view of a question with a non-existing ID in database
        returns a 404 not found.
        """
        id = 1000  # Non-existing ID
        url = reverse('polls:detail', args=(id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_question(self):
        """
        Get single question by id
        """
        question = create_question(question_text='Question.', days=-5)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question)
    

class QuestionVoteViewTests(TestCase):
    def test_question_with_non_existing_id(self):
        """
        The vote view of a question with a non-existing ID in database
        returns a 404 not found.
        """
        id = 1000  # Non-existing ID
        url = reverse('polls:vote', args=(id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_vote_redirects_to_results_page(self):
        """
        The vote view redirects to the results page after successful voting
        """
        question = create_question(question_text="Question.", days=-30)
        choice1 = create_choice(choice_text="Choice 1", question=question)
        url = reverse('polls:vote', args=(question.id,))
        response = self.client.post(url, {"choice": choice1.id})
        self.assertRedirects(response, reverse('polls:results', args=(question.id,)))

    def test_question_choice_votes_is_zero_initially(self):
        """
        The votes count is zero when choice is created
        """
        question = create_question(question_text="Question.", days=-30)
        choice1 = create_choice(choice_text="Choice 1", question=question)
        self.assertEqual(choice1.votes, 0)

    def test_question_choice_votes_increases_after_vote(self):
        """
        The votes count is increased by 1 after successful voting
        """
        question = create_question(question_text="Question.", days=-30)
        choice1 = create_choice(choice_text="Choice 1", question=question)

        url = reverse('polls:vote', args=(question.id,))
        self.client.post(url, {"choice": choice1.id})
        choice1_updated = get_choice(choice1.id)
        self.assertEqual(choice1_updated.votes, choice1.votes + 1)

    def test_question_with_non_existing_choice_id(self):
        """
        The vote view of a question with a choice ID not existing in database
        returns a 404 not found.
        """
        question = create_question(question_text="Question.", days=-30)
        choice_id = 2000
        url = reverse('polls:vote', args=(question.id,))
        response = self.client.post(url, {"choice": choice_id})
        self.assertTemplateUsed(response, 'polls/detail.html')
        self.assertContains(response, question)


class QuestionResultsViewTests(TestCase):
    def test_question_with_non_existing_id(self):
        """
        The results view of a question with a non-existing ID in database
        returns a 404 not found.
        """
        id = 1000  # Non-existing ID
        url = reverse('polls:results', args=(id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_with_choices_loaded_in_results_page(self):
        """
        Load choices of questions in results page
        """
        question = create_question(question_text="Question.", days=-30)
        choice1 = create_choice(choice_text="Choice 1", question=question)
        choice2 = create_choice(choice_text="Choice 2", question=question)
        choice3 = create_choice(choice_text="Choice 3", question=question)
        url = reverse('polls:results', args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(list(response.context["question"].question_choices.all()), [choice1, choice2, choice3])
        