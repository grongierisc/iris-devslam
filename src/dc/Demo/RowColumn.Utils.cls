/// Description
Class RowColumn.Utils
{

/// Description
ClassMethod AppendLastVector() As %Status
{
    Set sc = $$$OK
    For i = "^CATa.BJqo.1.V1","^CATa.BJqo.1.V2","^CATa.BJqo.1.V3","^CATa.BJqo.1.V4" {
        set max = ""
        while $order(@i@(max)) '= "" {
            set max = $order(@i@(max))
        }
        if max >1 {
            set @i@(max+1) = @i@(max)
            set @i@(max) = @i@(max-1)
        }
        else {
            set @i@(max+1) = @i@(max)
        }

    }
    Return sc
}

ClassMethod AppendLastVectorMix() As %Status
{
    Set sc = $$$OK
    For i = "^CATa.CfQt.1.V1" {
        set max = ""
        while $order(@i@(max)) '= "" {
            set max = $order(@i@(max))
        }
        if max >1 {
            set @i@(max+1) = @i@(max)
            set @i@(max) = @i@(max-1)
        }
        else {
            set @i@(max+1) = @i@(max)
        }
    }
    Return sc
}

}
