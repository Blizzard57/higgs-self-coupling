ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c      written by the UFO converter
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc

      SUBROUTINE COUP1()

      IMPLICIT NONE
      INCLUDE 'model_functions.inc'

      DOUBLE PRECISION PI, ZERO
      PARAMETER  (PI=3.141592653589793D0)
      PARAMETER  (ZERO=0D0)
      INCLUDE 'input.inc'
      INCLUDE 'coupl.inc'
      GC_69 = -6.000000D+00*MDL_COMPLEXI*MDL_LAM*MDL_V
      GC_70 = (MDL_EE__EXP__2*MDL_COMPLEXI*MDL_V)/(2.000000D+00
     $ *MDL_SW__EXP__2)
      END
