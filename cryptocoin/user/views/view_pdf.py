from .views_global import *
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponse


def pdf_codes_admin(request):
    if not request.user.is_authenticated or request.user.is_superuser:
        return HttpResponseRedirect(reverse('user:index'))
    ud = get_object_or_404(UserData, username=request.user.username)
    if not ud.is_admin:
        return HttpResponseRedirect(reverse('user:index'))

    # get the name of codes and codes themselves
    code_name = request.POST.get('codeName')
    data = []
    n = 5
    if code_name == 'award':
        data = Code.objects.filter(school=ud.school, name='award')
        # n = 4
    elif code_name == 'registration':
        data = Code.objects.filter(school=ud.school, name='registration')  # .values_list('allowed_hash', flat=True)
    else:
        messages.warning(request, 'The code request should be either for registration or reward codes')
        return HttpResponseRedirect(reverse('user:code-generator'))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50, pagesize=letter)
    elements = []
    # create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="codes_' + code_name + '.pdf"'

    # draw codes on the pdf
    if data:
        # split 1d data into 2d
        data = [data[i:i + n] for i in range(0, len(data), n)]
        # create and draw the table
        t = Table(data)
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
        ]))
        elements.append(t)
        # write the document to disk
        doc.build(elements)

        # get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    else:
        messages.warning(request, 'No codes available')
        return HttpResponseRedirect(reverse('user:code-generator'))
