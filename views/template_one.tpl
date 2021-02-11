<%
if admin:
    include('header_admin.tpl', title=title)
else: 
    include('header.tpl', title=title)
end
%>
<body>
  %include('content.tpl')
</body>

% include('footer.tpl')

