using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class CatController : MonoBehaviour
{
    [SerializeField]
    private NavMeshAgent cat;
    [SerializeField]
    private Vector3 destination;

    DoorFuntionality doorFunc;
    bool started;

    // Start is called before the first frame update
    void Start()
    {
        doorFunc = FindObjectOfType<DoorFuntionality>();
    }

    // Update is called once per frame
    void Update()
    {
        if (doorFunc.fridgeOpened && !started)
        {
            started = true;
            StartCoroutine(moveCat(new Vector3(), destination));
        }

    }

    public IEnumerator moveCat(Vector3 firstPos, Vector3 secPos)
    {

        if(this.gameObject.name == "BatObject")
        {
            //Bat
            cat.SetDestination(firstPos);
            yield return new WaitForSeconds(2.5f);
            cat.SetDestination(-secPos);
            yield return new WaitForSeconds(4f);
            cat.SetDestination(new Vector3(secPos.z, secPos.y, secPos.x));
            yield return new WaitForSeconds(4f);
            cat.SetDestination(secPos);
            
        }
        else
        {
            //Cat
            cat.SetDestination(firstPos);
            yield return new WaitForSeconds(2.5f);
            cat.SetDestination(secPos);
            yield return new WaitForSeconds(4f);
            cat.SetDestination(-secPos);
            yield return new WaitForSeconds(4f);
            cat.SetDestination(new Vector3(secPos.z, secPos.y, secPos.x));
        }
        
    }
}
