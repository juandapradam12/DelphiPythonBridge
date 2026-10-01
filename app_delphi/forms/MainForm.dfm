object Form1: TForm1
  Left = 0
  Top = 0
  Caption = 'Delphi-Python Bridge'
  ClientHeight = 400
  ClientWidth = 600
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OnCreate = FormCreate
  TextHeight = 13
  object Memo1: TMemo
    Left = 0
    Top = 0
    Width = 600
    Height = 365
    Align = alClient
    ScrollBars = ssBoth
    TabOrder = 0
    ExplicitWidth = 598
    ExplicitHeight = 357
  end
  object BtnRun: TButton
    Left = 0
    Top = 365
    Width = 600
    Height = 35
    Align = alBottom
    Caption = 'Run Python Processing'
    TabOrder = 1
    OnClick = BtnRunClick
    ExplicitTop = 357
    ExplicitWidth = 598
  end
end
