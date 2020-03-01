from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookForm

import datetime

def index(request):
    """
    Función vista para la página inicio del sitio.
    """
    # Genera contadores de algunos de los objetos principales
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Libros disponibles (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count() # El 'all()' está implicito por defecto

    genre_count = {}
    for genre in Genre.objects.all():
        num_book_genre = Book.objects.filter(genre__exact=genre).count()
        genre_count[genre]=num_book_genre

    # Numero de visitas para esta vista, como conteo en la variable de session.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    _context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'genre_count': genre_count,
        'num_visits': num_visits
    }

    # Renderiza la plantilla HTML index.html con los datos en la variable contexto
    return render(request, 'catalog/index.html', context=_context)

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian.
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    #if this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with from the request (binding):
        form = RenewBookForm(request.POST)
        # Check if the form is valid:
        if form.is_valid():
            #Process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            #Redirect to a new URL:
            return redirect('loaned-books')
    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    return render(request, 'catalog/book_renew_librarian.html', context={'form': form, 'bookinst': book_inst})

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 20

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """
    Generic class-based view listing book on loan to users.
    """
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/loaned_books.html'
    paginate_by = 10

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    template_name = 'catalog/create_change_form.html'
    permission_required = 'catalog.can_add_author'
    extra_context = {
        'title_window': 'Nuevo autor',
        'title_page': 'Agragar autor',
    }

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'catalog/create_change_form.html'
    permission_required = 'catalog.change_author'
    extra_context = {
        'title_window': 'Editar autor',
        'title_page': 'Editar autor',
    }

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'catalog/confirm_delete.html'
    permission_required = 'catalog.delete_author'
    extra_context = {
        'title_window': 'Eliminar autor',
        'title_page': 'Eliminar autor',
        'confirm_message': 'Está seguro que desea eliminar al autor',#sin signos, la plantilla los incluirá
    }

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    template_name = 'catalog/create_change_form.html'
    permission_required = 'catalog.add_book'
    extra_context = {
        'title_window': 'Nuevo libro',
        'title_page': 'Agragar libro',
    }

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    template_name = 'catalog/create_change_form.html'
    permission_required = 'catalog.change_book'
    extra_context = {
        'title_window': 'Editar libro',
        'title_page': 'Editar lirbo',
    }

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    template_name = 'catalog/confirm_delete.html'
    permission_required = 'catalog.delete_book'
    extra_context = {
        'title_window': 'Eliminar libro',
        'title_page': 'Eliniar libro',
        'confirm_message': 'Está seguro que desea eliminar el libro',
    }
