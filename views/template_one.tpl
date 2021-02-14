<%
if admin:
    include('header_admin.tpl', title=title)
else: 
    include('header.tpl', title=title)
end
%>
<body>
  <a href="{{path}}">HOME</a>
  <a href="{{path}}/admin">ADMIN</a>

  %include('content.tpl')
</body>
% include('footer.tpl')

