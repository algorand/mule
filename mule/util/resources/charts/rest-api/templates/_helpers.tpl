{{- define "fullname" -}}
{{- printf "%s" .Values.application_name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "hostname" -}}
{{- if .Values.ingress.base_name }}
{{- printf "%s.%s.%s" .Values.ingress.base_name .Values.environment .Values.ingress.domain -}}
{{- else -}}
{{- printf "%s.%s.%s" .Values.application_name .Values.environment .Values.ingress.domain -}}
{{- end -}}
{{- end -}}
