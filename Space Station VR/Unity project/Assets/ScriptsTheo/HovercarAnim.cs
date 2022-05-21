using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HovercarAnim : MonoBehaviour
{
    [SerializeField]
    private Vector3 startPos;
    [SerializeField]
    private Vector3 endPos;


    // Start is called before the first frame update
    void Start()
    {
        //StartCoroutine(Floating());
    }

    public IEnumerator Floating()
    {
        float index = 0;
        bool increase = true;
        float increasingFactor = 0.0001f;
        while (true)
        {
            transform.position = Vector3.Lerp(startPos, endPos, index);
            if(increase)
            {
                if(index < 0.25f)
                {
                    if(increasingFactor < 0.01f)
                    {
                        increasingFactor += 0.0002f;
                    }   
                }
                else if(index < 0.5f)
                {
                    if (increasingFactor < 0.01f)
                    {
                        increasingFactor += 0.0002f;
                    }
                }
                else if(index > 0.75f)
                {
                    if (increasingFactor > 0.0001f)
                    {
                        increasingFactor -= 0.0002f;
                    }
                }
                index += increasingFactor;

            }
            else
            {
                if (index < 0.25f)
                {
                    if (increasingFactor > 0.0001f)
                    {
                        increasingFactor -= 0.0002f;
                    }
                }
                else if (index < 0.5f)
                {
                    if (increasingFactor < 0.01f)
                    {
                        increasingFactor += 0.0002f;
                    }
                }
                else if (index > 0.75f)
                {
                    if (increasingFactor < 0.01f)
                    {
                        increasingFactor += 0.0002f;
                    }
                }
                index -= increasingFactor;
            }

            if(index > 1)
            {
                increase = false;
            }
            if(index < 0)
            {
                increase = true;
            }
            yield return new WaitForSeconds(Time.deltaTime*2f);
        }
    }
}
