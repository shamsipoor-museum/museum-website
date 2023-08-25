---
title: {{title}}
header: {{header}}
author: M. MAD
pic: {{pic}}
name: {{table.name}}
born: {{table.born}}
died: {{table.died}}
nationality: {{table.nationality}}
alma_mater: {{table.alma_mater}}
known_for: {{table.known_for}}
awards: {{table.awards}}
tags: {{table.tags}}
---
{%-  for paragraph in bio %}
{{paragraph}}

{%- endfor %}
