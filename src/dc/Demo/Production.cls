Class dc.Demo.Production Extends Ens.Production
{

XData ProductionDefinition
{
<Production Name="dc.Demo.Production" TestingEnabled="true" LogGeneralTraceEvents="false">
  <Description></Description>
  <ActorPoolSize>2</ActorPoolSize>
  <Item Name="Python.FileOperation" Category="" ClassName="Python.FileOperation" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="true" Schedule="">
    <Setting Target="Adapter" Name="Charset">utf-8</Setting>
    <Setting Target="Adapter" Name="FilePath">/irisdev/app/output/</Setting>
    <Setting Target="Host" Name="%settings">path=/irisdev/app/output/</Setting>
  </Item>
  <Item Name="Python.RedditService" Category="" ClassName="Python.RedditService" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
    <Setting Target="Host" Name="%classpaths">/irisdev/app/src/python/Reddit|/irisdev/app/src/python/Demo</Setting>
    <Setting Target="Host" Name="%settings">limit=10</Setting>
  </Item>
  <Item Name="Python.FilterPostRoutingRule" Category="" ClassName="Python.FilterPostRoutingRule" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
  </Item>
</Production>
}

}
