{{/*
Common labels
*/}}
{{- define "flask-aws-monitor.labels" -}}
app: {{ .Release.Name }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "flask-aws-monitor.selectorLabels" -}}
app: {{ .Release.Name }}
{{- end }}

{{/*
Image name
*/}}
{{- define "flask-aws-monitor.image" -}}
{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}
{{- end }}

