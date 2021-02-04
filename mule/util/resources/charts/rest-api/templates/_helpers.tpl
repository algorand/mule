{{- define "fullname" -}}
{{- printf "%s" .Values.application_name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "hostname" -}}
{{- printf "%s.%s.%s" .Values.application_name .Values.environment .Values.ingress.domain -}}
{{- end -}}
