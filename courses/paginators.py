from rest_framework.pagination import PageNumberPagination

class CoursePagination(PageNumberPagination):
    page_size = 6  # Количество элементов на странице
    page_size_query_param = 'page_size'  # Параметр запроса для указания количества элементов на странице
    max_page_size = 30  # Максимальное количество элементов на странице


class LessonPagination(PageNumberPagination):
    page_size = 10  # Количество элементов на странице
    page_size_query_param = 'page_size'  # Параметр запроса для указания количества элементов на странице
    max_page_size = 50  # Максимальное количество элементов на странице